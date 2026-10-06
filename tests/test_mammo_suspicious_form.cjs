// Run: node tests/test_mammo_suspicious_form.cjs (requires playwright and Edge)
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '../tool/mammo-suspicious-form.html'), 'utf8');
const FIXTURE_DIR = path.join(__dirname, 'fixtures/mammo_form');
const FIXTURES = ['cat0_unilateral', 'cat0_bilateral', 'cat0_benign_calc', 'cat4', 'cat5', 'cat2'];
const fixture = name => ({
    text: fs.readFileSync(path.join(FIXTURE_DIR, `${name}.txt`), 'utf8'),
    expected: JSON.parse(fs.readFileSync(path.join(FIXTURE_DIR, `${name}.expected.json`), 'utf8'))
});
// Served from a synthetic origin so that storage APIs are available to inspect.
const PAGE_URL = 'http://mammo-form.localhost/tool/mammo-suspicious-form.html';
const GEMINI = 'https://generativelanguage.googleapis.com/**';
const SCREENSHOT_DIR = process.env.MAMMO_SCREENSHOT_DIR || '';

const PAYLOAD = {
    source: 'rad-workflow/mammo-form', version: '1', chartNo: '00000001',
    nameZh: '王小美', nameEn: 'WANG^HSIAO MEI', birthDate: '19650309', studyDate: '20261006',
    accession: 'SYNTH0001', reportText: '(BI-RADS category 0, need additional imaging evaluation)'
};

const pageCount = p => p.locator('.form-page').count();
const isChecked = (p, pageIndex, key) =>
    p.locator('.form-page').nth(pageIndex).locator(`input[data-k="${key}"]`).isChecked();
const checkedKeys = (p, pageIndex) => p.evaluate(i =>
    Array.from(document.querySelectorAll('.form-page')[i].querySelectorAll('input[type=checkbox]:checked'))
        .map(el => el.dataset.k), pageIndex);
const fieldValue = (p, f, pageIndex = 0) =>
    p.locator('.form-page').nth(pageIndex).locator(`input[data-f="${f}"]`).inputValue();
const geminiBody = text => ({ candidates: [{ content: { parts: [{ text }] } }] });

async function loadFixture(p, name) {
    const { text, expected } = fixture(name);
    await p.evaluate(([t, e]) => {
        document.getElementById('reportText').value = t;
        applyParsedData(e);
    }, [text, expected]);
    return expected;
}

(async () => {
    const browser = await chromium.launch({ headless: true, channel: process.env.LDCT_BROWSER || 'msedge' });
    let failed = 0;
    let passed = 0;
    async function test(name, run, { init } = {}) {
        const page = await browser.newPage();
        const errors = [];
        const geminiRequests = [];
        page.on('pageerror', e => errors.push(e.message));
        page.on('request', r => { if (r.url().includes('generativelanguage.googleapis.com')) geminiRequests.push(r); });
        await page.route('**/*', route => (route.request().url() === PAGE_URL
            ? route.fulfill({ status: 200, contentType: 'text/html; charset=utf-8', body: html })
            : route.abort()));
        if (init) await page.addInitScript(init);
        try {
            await page.goto(PAGE_URL);
            await run(page, { geminiRequests });
            assert.deepEqual(errors, [], '瀏覽器不可出現未處理的錯誤');
            passed++;
            console.log(`PASS ${name}`);
        } catch (e) {
            failed++;
            console.error(`FAIL ${name}: ${e.message}`);
        } finally { await page.close(); }
    }

    try {
        // ---------- Import ----------
        await test('有效 payload 帶入病歷號、姓名、民國日期與報告', async p => {
            assert.equal(await p.evaluate(pl => importPayload(pl), PAYLOAD), true);
            assert.equal(await fieldValue(p, 'chartNo'), '00000001');
            assert.equal(await fieldValue(p, 'name'), '王小美');
            assert.equal(await p.locator('.form-page input[data-f="name"].needs-check').count(), 0);
            assert.deepEqual([await fieldValue(p, 'by'), await fieldValue(p, 'bm'), await fieldValue(p, 'bd')], ['54', '3', '9']);
            assert.deepEqual([await fieldValue(p, 'sy'), await fieldValue(p, 'sm'), await fieldValue(p, 'sd')], ['115', '10', '6']);
            assert.equal(await p.locator('#reportText').inputValue(), PAYLOAD.reportText);
            assert.equal(await isChecked(p, 0, 'cat0'), true);
        });
        await test('貼上純文字 "hello" 顯示錯誤且欄位不變', async p => {
            await p.evaluate(pl => importPayload(pl), PAYLOAD);
            await p.locator('.form-page input[data-k="i1"]').check();
            await p.evaluate(() => {
                const dt = new DataTransfer();
                dt.setData('text/plain', 'hello');
                document.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true }));
            });
            assert.equal(await p.locator('#status.error').count(), 1);
            assert.match(await p.locator('#status').innerText(), /不是本工具/);
            assert.equal(await fieldValue(p, 'chartNo'), '00000001');
            assert.equal(await fieldValue(p, 'name'), '王小美');
            assert.equal(await p.locator('#reportText').inputValue(), PAYLOAD.reportText);
            assert.equal(await isChecked(p, 0, 'i1'), true);
            assert.equal(await p.evaluate(() => importPayload('hello')), false);
        });
        await test('Ctrl+V 貼上 payload 可匯入；焦點在輸入框時不攔截', async p => {
            const paste = text => p.evaluate(t => {
                const dt = new DataTransfer();
                dt.setData('text/plain', t);
                (document.activeElement || document).dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true }));
            }, text);
            await p.locator('#reportText').focus();
            await paste(JSON.stringify(PAYLOAD));
            assert.equal(await fieldValue(p, 'chartNo'), '');
            await p.evaluate(() => document.activeElement.blur());
            await paste(JSON.stringify(PAYLOAD));
            assert.equal(await fieldValue(p, 'chartNo'), '00000001');
        });
        await test('中文姓名缺漏時以英文姓名帶入並標示需人工修正', async p => {
            await p.evaluate(pl => importPayload({ ...pl, nameZh: '', nameEn: 'CHEN^MEI' }), PAYLOAD);
            assert.equal(await fieldValue(p, 'name'), 'CHEN MEI');
            assert.equal(await p.locator('.form-page input[data-f="name"].needs-check').count(), 1);
            await p.locator('.form-page input[data-f="name"]').fill('陳美');
            assert.equal(await p.locator('.form-page input[data-f="name"].needs-check').count(), 0);
        });
        await test('匯入後 localStorage／sessionStorage 為空，網址不含病人資料', async p => {
            await p.evaluate(pl => importPayload(pl), PAYLOAD);
            await p.evaluate(() => applyParsedData({ lesions: [{ type: 'mass', side: 'R' }] }));
            const r = await p.evaluate(() => ({ ls: localStorage.length, ss: sessionStorage.length, url: location.href }));
            assert.deepEqual(r, { ls: 0, ss: 0, url: PAGE_URL });
            const dbs = await p.evaluate(async () => (indexedDB.databases ? (await indexedDB.databases()).length : 0));
            assert.equal(dbs, 0);
        });
        await test('「從剪貼簿匯入」按鈕讀取剪貼簿', async p => {
            await p.getByRole('button', { name: '從剪貼簿匯入', exact: true }).click();
            await p.waitForFunction(() => document.querySelector('.form-page input[data-f="chartNo"]').value === '00000001');
        }, { init: `navigator.clipboard.readText = async () => ${JSON.stringify(JSON.stringify(PAYLOAD))};` });
        await test('剪貼簿無權限時提示改按 Ctrl+V', async p => {
            await p.getByRole('button', { name: '從剪貼簿匯入', exact: true }).click();
            await p.waitForFunction(() => document.getElementById('status').classList.contains('error'));
            assert.match(await p.locator('#status').innerText(), /Ctrl\+V/);
        }, { init: `navigator.clipboard.readText = async () => { throw new Error('denied'); };` });

        // ---------- Dates and header ----------
        await test('toRocDate 範例表', async p => {
            const r = await p.evaluate(() => ['20261006', '1965.03.09', '1950/12/31', 'abc', '', '2026-1-5', '20260231'].map(toRocDate));
            assert.deepEqual(r, [{ y: '115', m: '10', d: '6' }, { y: '54', m: '3', d: '9' }, { y: '39', m: '12', d: '31' },
                null, null, { y: '115', m: '1', d: '5' }, null]);
            await p.evaluate(pl => importPayload({ ...pl, birthDate: 'abc' }), PAYLOAD);
            assert.deepEqual([await fieldValue(p, 'by'), await fieldValue(p, 'bm'), await fieldValue(p, 'bd')], ['', '', '']);
        });
        await test('表頭預設：佳里奇美醫院、放射科醫師空白、身分證 10 格空白且可編輯', async p => {
            await p.locator('.form-page input[data-f="physician"]').fill('X');
            await p.locator('.form-page input[data-f="id0"]').fill('A');
            await p.evaluate(pl => importPayload(pl), PAYLOAD);
            assert.equal(await fieldValue(p, 'hospital'), '佳里奇美醫院');
            assert.equal(await fieldValue(p, 'physician'), '');
            const ids = await p.locator('.form-page input.idbox').evaluateAll(els => els.map(e => e.value));
            assert.deepEqual(ids, Array(10).fill(''));
            await p.locator('.form-page input[data-f="id0"]').fill('A');
            await p.locator('.form-page input[data-f="physician"]').fill('醫師');
            assert.equal(await fieldValue(p, 'id0'), 'A');
            assert.equal(await fieldValue(p, 'physician'), '醫師');
        });

        // ---------- Category ----------
        await test('detectCategory 範例表與警告', async p => {
            const r = await p.evaluate(() => [
                'BI-RADS category 0', 'BI-RADS Category 4', 'BI-RADS assessment:\nCategory 4C (Suspicious...)',
                'BI-RADS category 2', 'no birads line here', 'BIRADS density C\nBI-RADS category 5', 'category: 3'
            ].map(detectCategory));
            assert.deepEqual(r, [{ category: 0, sub: null }, { category: 4, sub: null }, { category: 4, sub: 'c' },
                { category: 2, sub: null }, { category: null, sub: null }, { category: 5, sub: null }, { category: 3, sub: null }]);
            const cats = ['cat0', 'cat3', 'cat4', 'cat4a', 'cat4b', 'cat4c', 'cat5'];
            const cases = [
                ['(BI-RADS category 0, need additional imaging evaluation)', ['cat0'], false],
                ['BI-RADS Category 4', ['cat4'], false],
                ['BI-RADS assessment:\nCategory 4C (Suspicious Abnormality)', ['cat4', 'cat4c'], false],
                ['BI-RADS category 2', [], true],
                ['No assessment line.', [], true]
            ];
            for (const [text, ticked, warn] of cases) {
                await p.locator('#reportText').fill(text);
                const on = [];
                for (const k of cats) if (await isChecked(p, 0, k)) on.push(k);
                assert.deepEqual(on, ticked, text);
                assert.equal(await p.locator('#catWarning.show').count(), warn ? 1 : 0, text);
            }
            await p.locator('.form-page input[data-k="cat3"]').check();
            assert.equal(await isChecked(p, 0, 'cat3'), true);
        });
        await test('6 份 fixture 的 category 與期望值一致', async p => {
            for (const name of FIXTURES) {
                const { text, expected } = fixture(name);
                const r = await p.evaluate(t => detectCategory(t), text);
                assert.equal(r.category, expected.category, name);
                if (expected.category === 4) assert.equal(r.sub, expected.cat4Sub, name);
            }
        });
        await test('Category 4 無字母時才用 LLM cat4Sub', async p => {
            await p.locator('#reportText').fill('BI-RADS category 4, suspicious');
            await p.evaluate(() => applyParsedData({ cat4Sub: 'b', lesions: [] }));
            assert.equal(await isChecked(p, 0, 'cat4b'), true);
            await p.locator('#reportText').fill('BI-RADS category 4A');
            await p.evaluate(() => applyParsedData({ cat4Sub: 'c', lesions: [] }));
            assert.equal(await isChecked(p, 0, 'cat4a'), true);
            assert.equal(await isChecked(p, 0, 'cat4c'), false);
        });

        // ---------- Lesion pages ----------
        await test('各 fixture 依 lesions 數產生頁數並勾選正確項目', async p => {
            const itemOf = { mass: 1, calcification: 2, asymmetry: 3, distortion: 4, skin_nipple: 5, axillary_ln: 6, ducts: 7, diffuse_skin: 8, other: 9 };
            for (const name of FIXTURES) {
                const expected = await loadFixture(p, name);
                assert.equal(await pageCount(p), Math.max(1, expected.lesions.length), name);
                for (let i = 0; i < expected.lesions.length; i++) {
                    const l = expected.lesions[i];
                    const n = itemOf[l.type];
                    assert.equal(await isChecked(p, i, `i${n}`), true, `${name} page ${i + 1} item ${n}`);
                    assert.equal(await isChecked(p, i, `i${n}.${l.side}`), true, `${name} page ${i + 1} side`);
                    const items = (await checkedKeys(p, i)).filter(k => /^i\d$/.test(k));
                    assert.deepEqual(items, [`i${n}`], `${name} page ${i + 1} only one item`);
                }
                if (!expected.lesions.length) {
                    assert.deepEqual((await checkedKeys(p, 0)).filter(k => k.startsWith('i')), [], name);
                }
            }
        });
        await test('雙側 fixture：第 1 頁 Mass Rt.、第 2 頁 Calcifications Lt.', async p => {
            await loadFixture(p, 'cat0_bilateral');
            assert.equal(await pageCount(p), 2);
            assert.deepEqual(await checkedKeys(p, 0), ['cat0', 'i1', 'i1.R', 'i1.size.1-2', 'i1.shape.irregular', 'i1.margin.indistinct', 'i1.density.equal']);
            assert.deepEqual(await checkedKeys(p, 1), ['cat0', 'i2', 'i2.L', 'i2.loc.UIQ', 'i2.distribution.grouped', 'i2.morphology.coarse_heterogeneous']);
            const titles = await p.locator('.form-page .fp-title').allInnerTexts();
            assert.equal(titles.length, 2);
        });
        await test('benign calcification fixture：只有 1 頁 Asymmetry Rt. Focal UOQ', async p => {
            await loadFixture(p, 'cat0_benign_calc');
            assert.equal(await pageCount(p), 1);
            assert.deepEqual(await checkedKeys(p, 0), ['cat0', 'i3', 'i3.R', 'i3.at.focal', 'i3.loc.UOQ']);
        });
        await test('cat4 fixture：Category 4 與 c 子分類、segmental fine pleomorphic', async p => {
            await loadFixture(p, 'cat4');
            assert.deepEqual(await checkedKeys(p, 0), ['cat4', 'cat4c', 'i2', 'i2.R', 'i2.loc.UOQ', 'i2.distribution.segmental', 'i2.morphology.fine_pleomorphic']);
        });
        await test('multiple_* 只勾在提供該選項的項目；other 文字帶入', async p => {
            await p.evaluate(() => applyParsedData({ lesions: [
                { type: 'mass', side: 'multiple_bilateral' },
                { type: 'asymmetry', side: 'multiple_unilateral' },
                { type: 'other', side: 'L', otherText: 'Skin lesion' }] }));
            assert.equal(await isChecked(p, 0, 'i1.mb'), true);
            assert.deepEqual(await checkedKeys(p, 1), ['i3']);
            assert.equal(await isChecked(p, 2, 'i9'), true);
            assert.equal(await p.locator('.form-page').nth(2).locator('input[data-t="i9.text"]').inputValue(), 'Skin lesion');
        });
        await test('validateParsed 丟棄未知 enum，結構錯誤回傳 null', async p => {
            const r = await p.evaluate(() => validateParsed({ cat4Sub: 'z', lesions: [{ type: 'mass', side: 'X',
                location: ['UOQ', 'upper-outer'], oneView: ['top'], shape: 'star', margin: 'spiculated', size: '5cm' }] }));
            assert.equal(r.cat4Sub, null);
            assert.deepEqual(r.lesions[0], { type: 'mass', side: null, location: ['UOQ'], oneView: [], otherText: null,
                size: null, shape: null, margin: 'spiculated', density: null, distribution: null, morphology: null, asymmetryType: null });
            assert.deepEqual(await p.evaluate(() => [validateParsed({ foo: 1 }), validateParsed({ lesions: 'x' }),
                validateParsed([]), validateParsed({ lesions: ['bad'] })]), [null, null, null, null]);
            await p.evaluate(() => applyParsedData({ lesions: [{ type: 'mass', side: 'X', shape: 'star' }] }));
            assert.deepEqual(await checkedKeys(p, 0), ['i1']);
        });
        await test('勾選可逐頁獨立編輯；表頭跨頁同步', async p => {
            await loadFixture(p, 'cat0_bilateral');
            await p.locator('.form-page').nth(1).locator('input[data-k="i4"]').check();
            assert.equal(await isChecked(p, 0, 'i4'), false);
            await p.locator('.form-page').nth(0).locator('input[data-f="physician"]').fill('甲醫師');
            assert.equal(await fieldValue(p, 'physician', 1), '甲醫師');
        });
        await test('刪除此頁與新增空白頁', async p => {
            await loadFixture(p, 'cat0_bilateral');
            await p.getByRole('button', { name: '新增空白頁', exact: true }).click();
            assert.equal(await pageCount(p), 3);
            assert.deepEqual(await checkedKeys(p, 2), ['cat0']);
            await p.getByRole('button', { name: '刪除此頁', exact: true }).first().click();
            assert.equal(await pageCount(p), 2);
            assert.equal(await isChecked(p, 0, 'i2.L'), true, '原第 2 頁成為第 1 頁');
            await p.getByRole('button', { name: '刪除此頁', exact: true }).first().click();
            await p.getByRole('button', { name: '刪除此頁', exact: true }).first().click();
            assert.equal(await pageCount(p), 1, '至少保留一頁');
        });

        // ---------- LLM path ----------
        await test('AI 解析：攔截 Gemini 回傳 fixture JSON 後產生頁面，只送報告文字', async (p, { geminiRequests }) => {
            const { text, expected } = fixture('cat0_bilateral');
            let body;
            await p.route(GEMINI, async route => {
                body = route.request().postDataJSON();
                await route.fulfill({ json: geminiBody(JSON.stringify({ cat4Sub: null, lesions: expected.lesions })) });
            });
            await p.evaluate(pl => importPayload(pl), { ...PAYLOAD, reportText: text });
            await p.locator('#apiKey').fill('SYNTHETIC_TEST_KEY');
            await p.getByRole('button', { name: 'AI 解析', exact: true }).click();
            await p.waitForFunction(() => document.getElementById('status').classList.contains('success'));
            assert.equal(await pageCount(p), 2);
            assert.equal(await isChecked(p, 1, 'i2.L'), true);
            assert.equal(geminiRequests.length, 1);
            assert.ok(geminiRequests[0].url().includes('/models/gemini-3.8-flash:generateContent'));
            assert.ok(!geminiRequests[0].url().includes('SYNTHETIC_TEST_KEY'), '金鑰不放網址');
            const sent = JSON.stringify(body);
            assert.equal(body.generationConfig.responseMimeType, 'application/json');
            for (const secret of ['00000001', '王小美', 'WANG', '19650309', '20261006', 'SYNTH0001']) assert.ok(!sent.includes(secret), secret);
            assert.ok(sent.includes('Grouped coarse heterogenous'));
            const ldct = fs.readFileSync(path.join(__dirname, '../tool/ldct-report.html'), 'utf8');
            assert.ok(ldct.includes("const modelId = 'gemini-3.8-flash'"), 'LDCT 模型 id 已變動，需同步');
        });
        await test('AI 解析：非 JSON 回應顯示錯誤與原始回應，勾選不變', async p => {
            await p.route(GEMINI, route => route.fulfill({ json: geminiBody('Sorry, I cannot do that.') }));
            await loadFixture(p, 'cat0_bilateral');
            const before = [await checkedKeys(p, 0), await checkedKeys(p, 1)];
            await p.locator('#apiKey').fill('SYNTHETIC_TEST_KEY');
            await p.getByRole('button', { name: 'AI 解析', exact: true }).click();
            await p.waitForFunction(() => document.getElementById('status').classList.contains('error'));
            assert.match(await p.locator('#status').innerText(), /JSON/);
            assert.equal(await p.locator('#rawResponse').inputValue(), 'Sorry, I cannot do that.');
            assert.equal(await p.locator('#rawBox').isVisible(), true);
            assert.deepEqual([await checkedKeys(p, 0), await checkedKeys(p, 1)], before);
        });
        await test('AI 解析：缺 lesions（{"foo":1}）顯示錯誤', async p => {
            await p.route(GEMINI, route => route.fulfill({ json: geminiBody('{"foo":1}') }));
            await loadFixture(p, 'cat0_benign_calc');
            await p.locator('#apiKey').fill('SYNTHETIC_TEST_KEY');
            await p.getByRole('button', { name: 'AI 解析', exact: true }).click();
            await p.waitForFunction(() => document.getElementById('status').classList.contains('error'));
            assert.match(await p.locator('#status').innerText(), /格式不符/);
            assert.equal(await p.locator('#rawResponse').inputValue(), '{"foo":1}');
            assert.equal(await pageCount(p), 1);
            assert.equal(await isChecked(p, 0, 'i3.at.focal'), true);
        });
        await test('AI 解析：缺金鑰時提示且不送出請求', async (p, { geminiRequests }) => {
            await p.locator('#reportText').fill('BI-RADS category 0');
            await p.getByRole('button', { name: 'AI 解析', exact: true }).click();
            assert.match(await p.locator('#status').innerText(), /Gemini API 金鑰/);
            await p.waitForTimeout(200);
            assert.equal(geminiRequests.length, 0);
        });
        await test('金鑰欄為 password，可切換顯示', async p => {
            assert.equal(await p.locator('#apiKey').getAttribute('type'), 'password');
            await p.getByRole('button', { name: '顯示', exact: true }).click();
            assert.equal(await p.locator('#apiKey').getAttribute('type'), 'text');
        });
        await test('prompt 位於標記之間並包含 schema 與規則', async () => {
            const m = html.match(/\/\* MAMMO-PROMPT-START \*\/\s*const MAMMO_SYSTEM_PROMPT = `([\s\S]*?)`;\s*\/\* MAMMO-PROMPT-END \*\//);
            assert.ok(m, '找不到 prompt 標記');
            for (const s of ['"multiple_bilateral"', '"fine_linear_branching"', '"Axillary tail"', 'benign', 'otherText', 'o\'clock', 'cat4Sub'])
                assert.ok(m[1].includes(s), s);
        });

        // ---------- Print ----------
        await test('列印媒體：只顯示表單頁、按鈕隱藏、每頁有標題', async p => {
            await p.evaluate(pl => importPayload(pl), { ...PAYLOAD, reportText: fixture('cat0_bilateral').text });
            await loadFixture(p, 'cat0_bilateral');
            if (SCREENSHOT_DIR) await p.screenshot({ path: path.join(SCREENSHOT_DIR, 'mammo_form_screen.png'), fullPage: true });
            await p.emulateMedia({ media: 'print' });
            for (const b of await p.locator('button').all()) assert.equal(await b.isVisible(), false);
            assert.equal(await p.locator('#apiKey').isVisible(), false);
            assert.equal(await p.locator('#reportText').isVisible(), false);
            const titles = p.locator('.form-page .fp-title');
            assert.equal(await titles.count(), 2);
            for (let i = 0; i < 2; i++) {
                assert.equal(await titles.nth(i).isVisible(), true);
                assert.equal(await titles.nth(i).innerText(), '健康署婦女乳房X光攝影檢查服務之篩檢疑似異常個案報告表');
            }
            const breaks = await p.evaluate(() => Array.from(document.querySelectorAll('.form-page')).map(e => getComputedStyle(e).breakAfter));
            assert.equal(breaks[0], 'page');
            if (SCREENSHOT_DIR) {
                await p.screenshot({ path: path.join(SCREENSHOT_DIR, 'mammo_form_print.png'), fullPage: true });
                await p.pdf({ path: path.join(SCREENSHOT_DIR, 'mammo_form_print.pdf'), format: 'A4', preferCSSPageSize: true, printBackground: true });
            }
            const pdf = await p.pdf({ format: 'A4', preferCSSPageSize: true });
            const pages = (pdf.toString('latin1').match(/\/Type\s*\/Page[^s]/g) || []).length;
            assert.equal(pages, 2, 'PDF 應剛好 2 頁 A4');
        });
    } finally { await browser.close(); }
    console.log(`${passed} passed, ${failed} failed`);
    process.exitCode = failed ? 1 : 0;
})().catch(e => { console.error(e); process.exitCode = 1; });
