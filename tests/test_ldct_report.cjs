// 執行：node tests/test_ldct_report.cjs（需安裝 playwright 與 Edge）
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, '../tool/ldct-report.html'), 'utf8');

(async () => {
    const browser = await chromium.launch({ headless: true, channel: process.env.LDCT_BROWSER || 'msedge' });
    let failed = 0;
    let passed = 0;
    async function test(name, run) {
        const page = await browser.newPage();
        const errors = [];
        page.on('pageerror', e => errors.push(e.message));
        await page.route('**/*', route => route.abort());
        try {
            await page.setContent(html);
            await run(page);
            assert.deepEqual(errors, [], '瀏覽器不可出現未處理的錯誤');
            passed++;
            console.log(`PASS ${name}`);
        } catch (e) {
            failed++;
            console.error(`FAIL ${name}: ${e.message}`);
        } finally { await page.close(); }
    }
    try {
        await test('四個獨立 checkbox 可同時勾選；可疑結節不被良性結節遮蔽', async p => {
            for (const label of ['No lung nodule', 'Benign features', 'Insignificant (<6mm)', 'Juxtapleural <10mm']) {
                await p.getByRole('checkbox', { name: label, exact: true }).check({ timeout: 1000 });
            }
            assert.equal(await p.getByRole('checkbox', { name: 'No lung nodule', exact: true }).isChecked(), true);
            const report = await p.evaluate(() => {
                applyParsedData({ lung_rads_category: '4B', benign_features: true,
                    has_significant_nodules: true, significant_count: '1',
                    significant_nodules: [{ size: '18', density: 'solid', lobe: 'RUL' }] });
                return generateTextReport();
            });
            assert.ok(report.includes('■Nodule with benign features.'));
            assert.ok(report.includes('Entire Nodule: 18 mm'));
        });
        await test('多個 insignificant nodules：AI 單一 IM 不可冒充完整清單', async p => {
            const fields = await p.evaluate(() => {
                document.getElementById('impressionText').value = 'Small nodules (Ser/Img: 2/4) (Ser/Img: 2/55)';
                applyParsedData({ insignificant_nodules: true, insignificant_series: '2', insignificant_image: '4' });
                return [document.getElementById('insigSeries').value, document.getElementById('insigImage').value];
            });
            assert.equal(fields[0], '2');
            assert.ok(fields[1] === '' || fields[1] === '4,55', 'IM 必須完整或空白');
        });
        await test('人工輸入多個 IM 完整保留', async p => {
            await p.locator('#insigSeries').fill('2');
            await p.locator('#insigImage').fill('4,55');
            assert.ok((await p.evaluate(() => generateTextReport())).includes('SE:2, IM:4,55'));
        });
        await test('再次解析清除舊發現與 S，保留病人及醫師附註', async p => {
            const result = await p.evaluate(() => {
                document.getElementById('patientName').value = 'SYNTHETIC';
                document.getElementById('pdfNote').value = '醫師附註';
                applyParsedData({ lung_rads_category: '2', emphysema: true, airway_nodule: true,
                    coronary_calcification: true, coronary_description: 'LAD', modifier_s: true,
                    other_lung: 'old finding', nodules_else: true, atypical_cyst: true, metastases_pattern: true });
                applyParsedData({ lung_rads_category: '1', no_nodule: true, emphysema: false,
                    coronary_calcification: false, modifier_s: false, other_lung: '' });
                return { checked: ['emphysema', 'coronaryCalcification', 'modifierS', 'airwayNodule',
                    'atypicalCyst', 'nodulesElse', 'metastasesPattern'].some(id => document.getElementById(id).checked),
                    other: document.getElementById('otherLungText').value,
                    name: document.getElementById('patientName').value, note: document.getElementById('pdfNote').value };
            });
            assert.deepEqual(result, { checked: false, other: '', name: 'SYNTHETIC', note: '醫師附註' });
        });
        await test('密度切換可輸入實心成分，切回 solid 後不輸出過時成分', async p => {
            await p.locator('#noduleSignificant').check();
            const row = p.locator('#noduleTableBody tr').first();
            await row.locator('td:nth-child(3) select').selectOption('part-solid');
            assert.equal(await row.locator('td:nth-child(4) input').isDisabled(), false);
            await row.locator('td:nth-child(4) input').fill('5');
            await row.locator('td:nth-child(4) input').dispatchEvent('change');
            assert.ok((await p.evaluate(() => generateTextReport())).includes('solid part: 5 mm'));
            await row.locator('td:nth-child(3) select').selectOption('solid');
            assert.equal(await row.locator('td:nth-child(4) input').isDisabled(), true);
            assert.ok(!(await p.evaluate(() => generateTextReport())).includes('solid part: 5 mm'));
        });
        await test('空結節陣列會清空畫面，再新增可以正常編輯', async p => {
            await p.evaluate(() => {
                applyParsedData({ has_significant_nodules: true, significant_nodules: [{ size: '18' }] });
                applyParsedData({ has_significant_nodules: false, significant_nodules: [] });
            });
            assert.equal(await p.locator('#noduleTableBody tr').count(), 0);
            await p.locator('#noduleSignificant').check();
            await p.getByRole('button', { name: '+ Add Nodule', exact: true }).click();
            await p.locator('#noduleTableBody tr td:nth-child(2) input').fill('8');
            await p.locator('#noduleTableBody tr td:nth-child(2) input').dispatchEvent('change');
            assert.ok((await p.evaluate(() => generateTextReport())).includes('Entire Nodule: 8 mm'));
        });
        await test('結節及 PDF 日期不解析輸入中的 HTML', async p => {
            const injected = await p.evaluate(() => {
                addNoduleRow({ srsImg: '\"><span id="injected-nodule">test</span><input value="' });
                document.getElementById('lungRadsCategory').value = '2';
                document.getElementById('examDate').value = '<img id="injected-date" src=x>';
                openPDFEditor();
                return !!document.querySelector('#injected-nodule, #injected-date');
            });
            assert.equal(injected, false);
        });
        await test('取消勾選其他發現後，PDF 不再採用殘留描述', async p => {
            const pdf = await p.evaluate(() => {
                document.getElementById('lungRadsCategory').value = '2';
                document.getElementById('otherAbdNeckDesc').value = 'thyroid nodule';
                return buildPatientNotificationHTML();
            });
            assert.ok(!pdf.includes('■ 甲狀腺腫大'));
        });
        await test('有勾選其他發現時，PDF 仍輸出對應項目', async p => {
            const pdf = await p.evaluate(() => {
                document.getElementById('lungRadsCategory').value = '2';
                document.getElementById('otherAbdNeck').checked = true;
                document.getElementById('otherAbdNeckDesc').value = 'thyroid nodule';
                return buildPatientNotificationHTML();
            });
            assert.ok(pdf.includes('■ 甲狀腺腫大'));
        });
        await test('AI 未提及 prior 時保留使用者日期及原本分類', async p => {
            const result = await p.evaluate(() => {
                document.getElementById('priorDate').value = '2025/01/02';
                applyParsedData({ lung_rads_category: '2', no_nodule: true, airway_nodule: true, airway_type: 'subsegmental' });
                return [document.getElementById('priorDate').value, document.getElementById('lungRadsCategory').value];
            });
            assert.deepEqual(result, ['2025/01/02', '2']);
        });
        await test('AI Parse 完整流程：多影像留 SE，第二次解析清除先前結果', async p => {
            const responses = [
                { lung_rads_category: '2', benign_features: true, insignificant_nodules: true,
                    insignificant_series: '2', insignificant_image: '4', emphysema: true },
                { lung_rads_category: '1', no_nodule: true, emphysema: false }
            ];
            await p.route('https://generativelanguage.googleapis.com/**', async route => {
                await route.fulfill({ json: { candidates: [{ content: { parts: [{ text: JSON.stringify(responses.shift()) }] } }] } });
            });
            await p.locator('#apiKey').fill('SYNTHETIC_TEST_KEY');
            await p.locator('#impressionText').fill('Small nodules (Ser/Img: 2/4) (Ser/Img: 2/55). Calcified granuloma. Emphysema.');
            await p.getByRole('button', { name: 'AI Parse', exact: true }).click();
            await p.waitForFunction(() => document.getElementById('aiStatus').classList.contains('success'));
            assert.equal(await p.locator('#insigSeries').inputValue(), '2');
            assert.equal(await p.locator('#insigImage').inputValue(), '');
            assert.equal(await p.locator('#noduleBenign').isChecked(), true);
            assert.equal(await p.locator('#noduleInsignificant').isChecked(), true);
            await p.locator('#impressionText').fill('No lung nodules.');
            await p.getByRole('button', { name: 'AI Parse', exact: true }).click();
            await p.waitForFunction(() => document.getElementById('lungRadsCategory').value === '1');
            assert.equal(await p.locator('#emphysema').isChecked(), false);
            assert.equal(await p.locator('#noduleBenign').isChecked(), false);
            assert.equal(await p.locator('#insigSeries').inputValue(), '');
            assert.ok((await p.locator('#reportPreview').innerText()).includes('■No lung nodule'));
        });
    } finally { await browser.close(); }
    console.log(`${passed} passed, ${failed} failed`);
    process.exitCode = failed ? 1 : 0;
})().catch(e => { console.error(e); process.exitCode = 1; });
