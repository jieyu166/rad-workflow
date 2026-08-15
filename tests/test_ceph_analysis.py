from __future__ import annotations

import html
import json
import re
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).parents[1]
HTML_PATH = ROOT / "tool" / "ceph-analysis.html"


class CephPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: dict[str, dict[str, str | None]] = {}
        self.external_assets: list[tuple[str, str]] = []
        self.core_script: list[str] = []
        self.app_script: list[str] = []
        self._script_target: str | None = None

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            self.elements[element_id] = attributes
        for attribute in ("src", "href"):
            value = attributes.get(attribute)
            if value:
                self.external_assets.append((attribute, value))
        if tag == "script" and not attributes.get("src"):
            self._script_target = (
                "core" if element_id == "ceph-analysis-core" else "app"
            )

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._script_target = None

    def handle_data(self, data: str) -> None:
        if self._script_target == "core":
            self.core_script.append(data)
        elif self._script_target == "app":
            self.app_script.append(data)


def parse_page() -> tuple[str, CephPageParser]:
    source = HTML_PATH.read_text(encoding="utf-8")
    parser = CephPageParser()
    parser.feed(source)
    return source, parser


def run_core(expression: str):
    _, parser = parse_page()
    source = "".join(parser.core_script)
    if not source.strip():
        raise AssertionError("ceph-analysis-core script is missing")
    program = r"""
const vm = require("node:vm");
const source = JSON.parse(process.argv[1]);
const expression = process.argv[2];
const context = vm.createContext({});
vm.runInContext(source, context);
process.stdout.write(JSON.stringify(vm.runInContext(expression, context)));
"""
    completed = subprocess.run(
        ["node", "-e", program, json.dumps(source), expression],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(completed.stdout)


def browser_path() -> Path:
    candidates = (
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    )
    browser = next((path for path in candidates if path.exists()), None)
    if browser is None:
        raise unittest.SkipTest("Chrome or Edge is required for UI verification")
    return browser


def run_browser_probe(
    probe_body: str,
    *,
    window_size: str = "1440,900",
) -> dict[str, object]:
    source, _ = parse_page()
    probe = f"""
<script>
(async () => {{
  let result;
  try {{
    result = await (async () => {{ {probe_body} }})();
  }} catch (error) {{
    result = {{ __error: String(error && error.stack || error) }};
  }}
  document.body.innerHTML = '<pre id="ceph-test-result">' +
    JSON.stringify(result) + '</pre>';
}})();
</script>
"""
    fixture = source.replace("</body>", probe + "</body>")
    with tempfile.TemporaryDirectory() as temp_dir:
        fixture_path = Path(temp_dir) / "ceph-fixture.html"
        fixture_path.write_text(fixture, encoding="utf-8")
        completed = subprocess.run(
            [
                str(browser_path()),
                "--headless=new",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-background-networking",
                "--no-first-run",
                "--virtual-time-budget=5000",
                f"--user-data-dir={Path(temp_dir) / 'profile'}",
                f"--window-size={window_size}",
                "--dump-dom",
                fixture_path.as_uri(),
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=20,
        )
    match = re.search(
        r'<pre id="ceph-test-result">(.*?)</pre>',
        completed.stdout,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("browser fixture did not return ceph-test-result")
    return json.loads(html.unescape(match.group(1)))


class CephHarnessContractTests(unittest.TestCase):
    def test_production_page_exposes_required_test_hooks(self) -> None:
        _, parser = parse_page()
        required_ids = {
            "ceph-app",
            "wizard-progress",
            "drop-zone",
            "image-file",
            "ceph-canvas",
            "current-step",
            "report-output",
            "aria-status",
        }

        for element_id in sorted(required_ids):
            with self.subTest(element_id=element_id):
                self.assertIn(
                    element_id,
                    parser.elements,
                    f"required DOM hook is missing: #{element_id}",
                )

    def test_core_harness_executes_production_script(self) -> None:
        self.assertEqual(run_core("typeof CephCore"), "object")

    def test_headless_fixture_executes_against_production_dom(self) -> None:
        result = run_browser_probe(
            "return { appPresent: Boolean(document.getElementById('ceph-app')) };"
        )

        self.assertEqual(result, {"appPresent": True})

    def test_offline_document_contract(self) -> None:
        source, parser = parse_page()
        image_file = parser.elements.get("image-file", {})

        self.assertFalse(
            parser.external_assets,
            f"external assets are forbidden: {parser.external_assets}",
        )
        self.assertTrue(
            "".join(parser.core_script).strip(),
            "ceph-analysis-core must be an inline production script",
        )
        self.assertTrue(
            "".join(parser.app_script).strip(),
            "the application must have an inline production script",
        )
        self.assertEqual(image_file.get("type"), "file")
        self.assertIn("image/png", image_file.get("accept") or "")
        self.assertIn("image/jpeg", image_file.get("accept") or "")
        for forbidden in (
            "fetch(",
            "XMLHttpRequest",
            "WebSocket",
            "localStorage",
            "indexedDB",
            "document.cookie",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(
                    forbidden,
                    source,
                    f"offline/privacy contract forbids {forbidden}",
                )

    def test_incisor_axis_guidance_uses_fdi_and_same_tooth_pairing(self) -> None:
        source, parser = parse_page()

        self.assertIn(
            "incisor-axis-guide",
            parser.elements,
            "the optional dental group needs an inline axis teaching aid",
        )
        for expected_text in (
            "一顆牙、兩個點、一條長軸",
            "FDI 11 或 21",
            "FDI 31 或 41",
            "切端與根尖必須來自同一顆牙",
            "無法可靠配對時，請標記不確定或跳過此組",
            "切端到根尖的連線，就是門牙長軸",
        ):
            with self.subTest(expected_text=expected_text):
                self.assertIn(expected_text, source)
        self.assertNotIn("#11/#21", source)


class CephImageIntakeTests(unittest.TestCase):
    def test_image_intake_contract(self) -> None:
        results = run_core(
            """[
              {type: 'image/png', size: 52428800, width: 16384, height: 9000},
              {type: 'image/jpeg', size: 1200, width: 2000, height: 16384},
              {type: 'text/plain', size: 100, width: 10, height: 10},
              {type: 'image/png', size: 52428801, width: 10, height: 10},
              {type: 'image/jpeg', size: 100, width: 16385, height: 10}
            ].map(CephCore.validateImageDescriptor)"""
        )

        self.assertEqual(
            [result["ok"] for result in results],
            [True, True, False, False, False],
        )
        self.assertEqual(
            [result.get("code") for result in results[2:]],
            ["unsupported-type", "file-too-large", "dimensions-too-large"],
        )

    def test_invalid_image_preserves_state(self) -> None:
        result = run_browser_probe(
            r"""
const bytes = Uint8Array.from(
  atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl9ZSoAAAAASUVORK5CYII='),
  char => char.charCodeAt(0)
);
const valid = new File([bytes], 'first.png', { type: 'image/png' });
const loaded = await CephApp.loadImageFile(valid);
const before = CephApp.getSnapshot();
const invalid = new File(['not an image'], 'notes.txt', { type: 'text/plain' });
const rejected = await CephApp.loadImageFile(invalid);
const after = CephApp.getSnapshot();
return {
  loaded,
  rejected,
  beforeName: before.imageName,
  afterName: after.imageName,
  afterWidth: after.imageWidth,
  errorText: document.getElementById('aria-status').textContent
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertTrue(result["loaded"]["ok"])
        self.assertFalse(result["rejected"]["ok"])
        self.assertEqual(result["rejected"]["code"], "unsupported-type")
        self.assertEqual(result["beforeName"], "first.png")
        self.assertEqual(result["afterName"], "first.png")
        self.assertEqual(result["afterWidth"], 1)
        self.assertIn("PNG", result["errorText"])

    def test_replacement_requires_confirmation(self) -> None:
        result = run_browser_probe(
            r"""
const bytes = Uint8Array.from(
  atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl9ZSoAAAAASUVORK5CYII='),
  char => char.charCodeAt(0)
);
await CephApp.loadImageFile(
  new File([bytes], 'first.png', { type: 'image/png' })
);
globalThis.confirm = () => false;
const replacement = await CephApp.loadImageFile(
  new File([bytes], 'second.png', { type: 'image/png' })
);
return {
  replacement,
  imageName: CephApp.getSnapshot().imageName,
  emptyHidden: document.getElementById('empty-state').hidden,
  nextEnabled: !document.getElementById('stage-next').disabled
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertFalse(result["replacement"]["ok"])
        self.assertEqual(result["replacement"]["code"], "replacement-cancelled")
        self.assertEqual(result["imageName"], "first.png")
        self.assertTrue(result["emptyHidden"])
        self.assertTrue(result["nextEnabled"])

    def test_dirty_study_registers_beforeunload_warning(self) -> None:
        result = run_browser_probe(
            r"""
const bytes = Uint8Array.from(
  atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl9ZSoAAAAASUVORK5CYII='),
  char => char.charCodeAt(0)
);
await CephApp.loadImageFile(
  new File([bytes], 'dirty.png', { type: 'image/png' })
);
const event = new Event('beforeunload', { cancelable: true });
const dispatchResult = globalThis.dispatchEvent(event);
return { dispatchResult, defaultPrevented: event.defaultPrevented };
"""
        )

        self.assertNotIn("__error", result)
        self.assertFalse(result["dispatchResult"])
        self.assertTrue(result["defaultPrevented"])


class CephLandmarkInteractionTests(unittest.TestCase):
    def test_coordinate_round_trip(self) -> None:
        result = run_core(
            """(() => {
              const image = {width: 2000, height: 1000};
              const viewport = {width: 1000, height: 800};
              const view = {zoom: 2, panX: 120, panY: -40};
              const source = {x: 0.25, y: 0.75};
              const display = CephCore.sourceToDisplay(
                source, image, viewport, view
              );
              return {
                display,
                restored: CephCore.displayToSource(
                  display, image, viewport, view
                )
              };
            })()"""
        )

        self.assertAlmostEqual(result["display"]["x"], 120)
        self.assertAlmostEqual(result["display"]["y"], 610)
        self.assertAlmostEqual(result["restored"]["x"], 0.25)
        self.assertAlmostEqual(result["restored"]["y"], 0.75)

    def test_landmark_history(self) -> None:
        result = run_browser_probe(
            r"""
const bytes = Uint8Array.from(
  atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl9ZSoAAAAASUVORK5CYII='),
  char => char.charCodeAt(0)
);
await CephApp.loadImageFile(
  new File([bytes], 'history.png', { type: 'image/png' })
);
CephApp.setLandmark('S', {x: 0.2, y: 0.3}, false);
CephApp.setLandmark('N', {x: 0.4, y: 0.5}, false);
CephApp.setLandmark('S', {x: 0.25, y: 0.35}, false);
CephApp.setLandmarkUncertain('S', true);
const changed = CephApp.getSnapshot();
CephApp.undo();
const uncertaintyUndone = CephApp.getSnapshot();
CephApp.undo();
const moveUndone = CephApp.getSnapshot();
CephApp.redo();
CephApp.redo();
CephApp.deleteLandmark('N');
const deleted = CephApp.getSnapshot();
CephApp.undo();
const restored = CephApp.getSnapshot();
return { changed, uncertaintyUndone, moveUndone, deleted, restored };
"""
        )

        self.assertNotIn("__error", result)
        self.assertTrue(result["changed"]["landmarks"]["S"]["uncertain"])
        self.assertFalse(
            result["uncertaintyUndone"]["landmarks"]["S"]["uncertain"]
        )
        self.assertAlmostEqual(
            result["moveUndone"]["landmarks"]["S"]["x"], 0.2
        )
        self.assertNotIn("N", result["deleted"]["landmarks"])
        self.assertIn("N", result["restored"]["landmarks"])
        self.assertEqual(result["restored"]["imageName"], "history.png")

    def test_canvas_pointer_uses_inverse_transform(self) -> None:
        result = run_browser_probe(
            r"""
const bytes = Uint8Array.from(
  atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl9ZSoAAAAASUVORK5CYII='),
  char => char.charCodeAt(0)
);
await CephApp.loadImageFile(
  new File([bytes], 'pointer.png', { type: 'image/png' })
);
CephApp.setView({zoom: 2, panX: 90, panY: -40});
CephApp.setActiveLandmark('A');
const canvas = document.getElementById('ceph-canvas');
const rect = canvas.getBoundingClientRect();
const snapshot = CephApp.getSnapshot();
const target = {x: 0.3, y: 0.6};
const display = CephCore.sourceToDisplay(
  target,
  {width: snapshot.imageWidth, height: snapshot.imageHeight},
  {width: rect.width, height: rect.height},
  snapshot.view
);
canvas.dispatchEvent(new PointerEvent('pointerdown', {
  clientX: rect.left + display.x,
  clientY: rect.top + display.y,
  button: 0,
  bubbles: true
}));
return CephApp.getSnapshot();
"""
        )

        self.assertNotIn("__error", result)
        self.assertAlmostEqual(result["landmarks"]["A"]["x"], 0.3, places=5)
        self.assertAlmostEqual(result["landmarks"]["A"]["y"], 0.6, places=5)
        self.assertEqual(result["activeLandmark"], "A")


class CephViewControlTests(unittest.TestCase):
    def test_view_controls_preserve_geometry(self) -> None:
        result = run_browser_probe(
            r"""
const bytes = Uint8Array.from(
  atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl9ZSoAAAAASUVORK5CYII='),
  char => char.charCodeAt(0)
);
await CephApp.loadImageFile(
  new File([bytes], 'view.png', { type: 'image/png' })
);
CephApp.setLandmark('S', {x: 0.2, y: 0.3}, false);
CephApp.setLandmark('N', {x: 0.7, y: 0.4}, true);
const before = CephApp.getSnapshot();
document.getElementById('zoom-in').click();
document.getElementById('zoom-in').click();
document.getElementById('invert-view').click();
const changed = CephApp.getSnapshot();
document.getElementById('fit-view').click();
const fitted = CephApp.getSnapshot();

CephApp.setActiveLandmark(null);
const canvas = document.getElementById('ceph-canvas');
const rect = canvas.getBoundingClientRect();
canvas.dispatchEvent(new PointerEvent('pointerdown', {
  clientX: rect.left + 200,
  clientY: rect.top + 200,
  button: 0,
  pointerId: 7,
  bubbles: true
}));
canvas.dispatchEvent(new PointerEvent('pointermove', {
  clientX: rect.left + 235,
  clientY: rect.top + 175,
  button: 0,
  pointerId: 7,
  bubbles: true
}));
canvas.dispatchEvent(new PointerEvent('pointerup', {
  clientX: rect.left + 235,
  clientY: rect.top + 175,
  button: 0,
  pointerId: 7,
  bubbles: true
}));
const panned = CephApp.getSnapshot();
document.getElementById('reset-view').click();
const reset = CephApp.getSnapshot();
return { before, changed, fitted, panned, reset };
"""
        )

        self.assertNotIn("__error", result)
        self.assertGreater(result["changed"]["view"]["zoom"], 1)
        self.assertTrue(result["changed"]["view"]["inverted"])
        self.assertEqual(result["fitted"]["view"]["zoom"], 1)
        self.assertEqual(result["fitted"]["view"]["panX"], 0)
        self.assertTrue(result["fitted"]["view"]["inverted"])
        self.assertAlmostEqual(result["panned"]["view"]["panX"], 35)
        self.assertAlmostEqual(result["panned"]["view"]["panY"], -25)
        self.assertEqual(
            result["before"]["landmarks"], result["reset"]["landmarks"]
        )
        self.assertEqual(
            result["reset"]["view"],
            {"zoom": 1, "panX": 0, "panY": 0, "inverted": False},
        )


class CephAccessibilityLayoutTests(unittest.TestCase):
    def test_accessibility_contract(self) -> None:
        _, parser = parse_page()

        self.assertEqual(parser.elements["ceph-canvas"].get("tabindex"), "0")
        self.assertTrue(parser.elements["ceph-canvas"].get("aria-label"))
        self.assertEqual(
            parser.elements["ceph-canvas"].get("aria-describedby"),
            "nudge-help",
        )
        self.assertIn("nudge-help", parser.elements)
        self.assertEqual(parser.elements["drop-zone"].get("role"), "button")
        self.assertEqual(parser.elements["drop-zone"].get("tabindex"), "0")
        self.assertEqual(parser.elements["aria-status"].get("role"), "status")
        self.assertEqual(parser.elements["aria-status"].get("aria-live"), "polite")
        self.assertTrue(parser.elements["report-output"].get("aria-label"))
        for button_id in (
            "choose-image",
            "zoom-out",
            "zoom-in",
            "fit-view",
            "invert-view",
            "reset-view",
            "undo-action",
            "redo-action",
            "stage-back",
            "stage-next",
            "copy-report",
            "generate-report",
        ):
            with self.subTest(button_id=button_id):
                self.assertEqual(parser.elements[button_id].get("type"), "button")

    def test_keyboard_only_landmark_refinement(self) -> None:
        result = run_browser_probe(
            r"""
const bytes = Uint8Array.from(
  atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl9ZSoAAAAASUVORK5CYII='),
  char => char.charCodeAt(0)
);
await CephApp.loadImageFile(
  new File([bytes], 'keyboard.png', { type: 'image/png' })
);
CephApp.setLandmark('S', {x: 0.5, y: 0.5}, false);
CephApp.setActiveLandmark('S');
const canvas = document.getElementById('ceph-canvas');
canvas.focus();
canvas.dispatchEvent(new KeyboardEvent('keydown', {
  key: 'ArrowRight',
  bubbles: true,
  cancelable: true
}));
return {
  snapshot: CephApp.getSnapshot(),
  status: document.getElementById('aria-status').textContent,
  focused: document.activeElement === canvas
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertAlmostEqual(
            result["snapshot"]["landmarks"]["S"]["x"], 0.501, places=6
        )
        self.assertAlmostEqual(
            result["snapshot"]["landmarks"]["S"]["y"], 0.5, places=6
        )
        self.assertIn("S", result["status"])
        self.assertTrue(result["focused"])

    def test_supported_desktop_layouts(self) -> None:
        for window_size in ("1440,900", "1024,768"):
            with self.subTest(window_size=window_size):
                result = run_browser_probe(
                    r"""
const viewer = document.querySelector('.viewer-card').getBoundingClientRect();
const sidebar = document.getElementById('current-step').getBoundingClientRect();
const progress = document.getElementById('wizard-progress').getBoundingClientRect();
const next = document.getElementById('stage-next').getBoundingClientRect();
return {
  clientWidth: document.documentElement.clientWidth,
  scrollWidth: document.documentElement.scrollWidth,
  viewerWidth: viewer.width,
  sidebarWidth: sidebar.width,
  progressWidth: progress.width,
  nextVisible: next.width > 0 && next.height > 0,
  sidebarRight: sidebar.right
};
""",
                    window_size=window_size,
                )

                self.assertNotIn("__error", result)
                self.assertLessEqual(result["scrollWidth"], result["clientWidth"])
                self.assertGreater(result["viewerWidth"], 300)
                self.assertGreater(result["sidebarWidth"], 280)
                self.assertGreater(result["progressWidth"], 600)
                self.assertTrue(result["nextVisible"])
                self.assertLessEqual(
                    result["sidebarRight"], result["clientWidth"] + 0.5
                )


class CephProgressiveWizardTests(unittest.TestCase):
    def test_progressive_unlock_and_skip(self) -> None:
        result = run_browser_probe(
            r"""
const bytes = Uint8Array.from(
  atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl9ZSoAAAAASUVORK5CYII='),
  char => char.charCodeAt(0)
);
const beforeImage = CephApp.goToStage('survey');
await CephApp.loadImageFile(
  new File([bytes], 'wizard.png', { type: 'image/png' })
);
const stageOrder = [];
for (const stage of ['survey', 'calibration', 'core']) {
  CephApp.goToStage(stage);
  stageOrder.push(CephApp.getSnapshot().currentStage);
}
const initially = {
  missing: document.getElementById('missing-core').textContent,
  reportDisabled: document.getElementById('generate-report').disabled,
  active: CephApp.getSnapshot().activeLandmark
};
for (const [key, point] of Object.entries({
  S: {x: 0.1, y: 0.2},
  N: {x: 0.3, y: 0.2},
  A: {x: 0.4, y: 0.5},
  B: {x: 0.45, y: 0.7}
})) {
  CephApp.setLandmark(key, point, false);
  CephApp.confirmActiveLandmark();
}
const complete = {
  missing: document.getElementById('missing-core').textContent,
  reportDisabled: document.getElementById('generate-report').disabled,
  nextDisabled: document.getElementById('stage-next').disabled,
  snapshot: CephApp.getSnapshot()
};
CephApp.goToStage('advanced');
CephApp.skipOptionalGroup('skeletal');
CephApp.skipOptionalGroup('dental');
const skipped = CephApp.getSnapshot();
return { beforeImage, stageOrder, initially, complete, skipped };
"""
        )

        self.assertNotIn("__error", result)
        self.assertFalse(result["beforeImage"])
        self.assertEqual(
            result["stageOrder"], ["survey", "calibration", "core"]
        )
        for key in ("S", "N", "A", "B"):
            self.assertIn(key, result["initially"]["missing"])
        self.assertTrue(result["initially"]["reportDisabled"])
        self.assertEqual(result["initially"]["active"], "S")
        self.assertEqual(result["complete"]["missing"], "核心四點已完成")
        self.assertFalse(result["complete"]["reportDisabled"])
        self.assertFalse(result["complete"]["nextDisabled"])
        self.assertTrue(result["skipped"]["optionalGroups"]["skeletal"])
        self.assertTrue(result["skipped"]["optionalGroups"]["dental"])
        for key in ("ANS", "PNS", "Go", "Me", "U1Tip", "U1Apex"):
            self.assertNotIn(key, result["skipped"]["landmarks"])

    def test_active_panel_matches_stage(self) -> None:
        result = run_browser_probe(
            r"""
const bytes = Uint8Array.from(
  atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl9ZSoAAAAASUVORK5CYII='),
  char => char.charCodeAt(0)
);
await CephApp.loadImageFile(
  new File([bytes], 'panels.png', { type: 'image/png' })
);
const visibleByStage = {};
for (const stage of ['survey', 'calibration', 'core']) {
  CephApp.goToStage(stage);
  visibleByStage[stage] = Array.from(
    document.querySelectorAll('[data-panel]')
  ).filter(panel => !panel.hidden).map(panel => panel.dataset.panel);
}
return {
  visibleByStage,
  current: document.querySelector('[aria-current="step"]').dataset.stage
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertEqual(result["visibleByStage"]["survey"], ["survey"])
        self.assertEqual(
            result["visibleByStage"]["calibration"], ["calibration"]
        )
        self.assertEqual(result["visibleByStage"]["core"], ["core"])
        self.assertEqual(result["current"], "core")

    def test_report_stage_contains_review_guidance(self) -> None:
        _, parser = parse_page()
        panel = parser.elements["report-step-panel"]
        self.assertEqual(panel.get("data-panel"), "report")
        html = HTML_PATH.read_text(encoding="utf-8")
        self.assertIn("最後複核", html)
        self.assertIn("不會靜默覆蓋人工文字", html)
        self.assertNotIn("完成核心四點後開放報告", html)

    def test_optional_group_guides_each_landmark(self) -> None:
        result = run_browser_probe(
            r"""
const bytes = Uint8Array.from(
  atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl9ZSoAAAAASUVORK5CYII='),
  char => char.charCodeAt(0)
);
await CephApp.loadImageFile(
  new File([bytes], 'advanced.png', { type: 'image/png' })
);
for (const [key, point] of Object.entries({
  S: {x: 0.1, y: 0.2}, N: {x: 0.3, y: 0.2},
  A: {x: 0.4, y: 0.5}, B: {x: 0.45, y: 0.7}
})) CephApp.setLandmark(key, point, false);
CephApp.goToStage('advanced');
CephApp.startOptionalGroup('skeletal');
const sequence = [];
for (const [key, point] of Object.entries({
  ANS: {x: 0.4, y: 0.3}, PNS: {x: 0.2, y: 0.3},
  Go: {x: 0.2, y: 0.8}, Me: {x: 0.5, y: 0.9}
})) {
  sequence.push(CephApp.getSnapshot().activeLandmark);
  CephApp.setLandmark(key, point, false);
  CephApp.confirmActiveLandmark();
}
return {
  sequence,
  snapshot: CephApp.getSnapshot(),
  guideHidden: document.getElementById('advanced-current').hidden,
  status: document.getElementById('optional-status').textContent
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertEqual(result["sequence"], ["ANS", "PNS", "Go", "Me"])
        self.assertIsNone(result["snapshot"]["activeLandmark"])
        self.assertTrue(result["guideHidden"])
        self.assertIn("骨性組：已完成", result["status"])


class CephSurveyTests(unittest.TestCase):
    def test_survey_defaults_and_batch_action(self) -> None:
        result = run_browser_probe(
            r"""
const initial = CephApp.getSnapshot().survey;
CephApp.setSurveyItem('tmj', 'abnormal', '右側髁突輪廓不規則');
CephApp.setSurveyItem('cervicalAirway', 'limited', '下緣未完整涵蓋');
globalThis.confirm = () => false;
const cancelled = CephApp.batchMarkSurveyNormal();
const afterCancel = CephApp.getSnapshot().survey;
globalThis.confirm = () => true;
const accepted = CephApp.batchMarkSurveyNormal();
const afterAccept = CephApp.getSnapshot().survey;
return { initial, cancelled, afterCancel, accepted, afterAccept };
"""
        )

        self.assertNotIn("__error", result)
        self.assertEqual(
            {item["status"] for item in result["initial"].values()},
            {"unassessed"},
        )
        self.assertFalse(result["cancelled"])
        self.assertEqual(result["afterCancel"]["imageQuality"]["status"], "unassessed")
        self.assertTrue(result["accepted"])
        self.assertEqual(result["afterAccept"]["tmj"]["status"], "abnormal")
        self.assertEqual(
            result["afterAccept"]["tmj"]["note"], "右側髁突輪廓不規則"
        )
        self.assertEqual(
            result["afterAccept"]["cervicalAirway"]["status"], "limited"
        )
        self.assertEqual(result["afterAccept"]["imageQuality"]["status"], "normal")
        self.assertEqual(result["afterAccept"]["sellaSkullBase"]["status"], "normal")

    def test_survey_controls_persist_explicit_status_and_note(self) -> None:
        result = run_browser_probe(
            r"""
const bytes = Uint8Array.from(
  atob('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl9ZSoAAAAASUVORK5CYII='),
  char => char.charCodeAt(0)
);
await CephApp.loadImageFile(
  new File([bytes], 'survey.png', { type: 'image/png' })
);
CephApp.goToStage('survey');
const status = document.getElementById('survey-jawsDentition-status');
const note = document.getElementById('survey-jawsDentition-note');
status.value = 'abnormal';
status.dispatchEvent(new Event('change', { bubbles: true }));
note.value = '左下顎角疑似局部骨質變化';
note.dispatchEvent(new Event('input', { bubbles: true }));
CephApp.goToStage('calibration');
CephApp.goToStage('survey');
return {
  survey: CephApp.getSnapshot().survey,
  statusValue: status.value,
  noteValue: note.value,
  rows: document.querySelectorAll('#survey-list .survey-row').length
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertEqual(result["rows"], 6)
        item = result["survey"]["jawsDentition"]
        self.assertEqual(item["status"], "abnormal")
        self.assertEqual(item["note"], "左下顎角疑似局部骨質變化")
        self.assertEqual(result["statusValue"], "abnormal")
        self.assertEqual(result["noteValue"], "左下顎角疑似局部骨質變化")


class CephCalibrationTests(unittest.TestCase):
    def test_scale_calibration_boundaries(self) -> None:
        result = run_core(
            """({
              valid: CephCore.calibrateScale(
                {x: 100, y: 200}, {x: 500, y: 200}, 40
              ),
              short: CephCore.calibrateScale(
                {x: 0, y: 0}, {x: 19, y: 0}, 40
              ),
              zero: CephCore.calibrateScale(
                {x: 0, y: 0}, {x: 400, y: 0}, 0
              ),
              negative: CephCore.calibrateScale(
                {x: 0, y: 0}, {x: 400, y: 0}, -1
              ),
              text: CephCore.calibrateScale(
                {x: 0, y: 0}, {x: 400, y: 0}, '40'
              )
            })"""
        )

        self.assertTrue(result["valid"]["ok"])
        self.assertAlmostEqual(result["valid"]["mmPerPixel"], 0.1)
        self.assertEqual(result["short"]["code"], "ruler-points-too-close")
        self.assertEqual(result["zero"]["code"], "invalid-distance")
        self.assertEqual(result["negative"]["code"], "invalid-distance")
        self.assertEqual(result["text"]["code"], "invalid-distance")

    def test_manual_distance_requires_scale(self) -> None:
        result = run_core(
            """({
              valid: CephCore.measureCalibratedDistance(
                'Airway AP', {x: 10, y: 20}, {x: 210, y: 20}, 0.1
              ),
              noScale: CephCore.measureCalibratedDistance(
                'Airway AP', {x: 10, y: 20}, {x: 210, y: 20}, null
              ),
              noLabel: CephCore.measureCalibratedDistance(
                '   ', {x: 10, y: 20}, {x: 210, y: 20}, 0.1
              ),
              samePoint: CephCore.measureCalibratedDistance(
                'Airway AP', {x: 10, y: 20}, {x: 10, y: 20}, 0.1
              )
            })"""
        )

        self.assertTrue(result["valid"]["ok"])
        self.assertEqual(result["valid"]["label"], "Airway AP")
        self.assertAlmostEqual(result["valid"]["valueMm"], 20.0)
        self.assertEqual(result["noScale"]["code"], "calibration-required")
        self.assertEqual(result["noLabel"]["code"], "label-required")
        self.assertEqual(result["samePoint"]["code"], "points-must-differ")

    def test_calibration_and_manual_distance_controls(self) -> None:
        result = run_browser_probe(
            r"""
const sourceCanvas = document.createElement('canvas');
sourceCanvas.width = 500;
sourceCanvas.height = 200;
const blob = await new Promise(resolve => sourceCanvas.toBlob(resolve, 'image/png'));
await CephApp.loadImageFile(
  new File([blob], 'ruler.png', { type: 'image/png' })
);
CephApp.goToStage('calibration');
CephApp.setCalibrationPoint('pointA', {x: 0.1, y: 0.5});
CephApp.setCalibrationPoint('pointB', {x: 0.9, y: 0.5});
const calibrated = CephApp.applyCalibration(40);
CephApp.setManualDistancePoint('pointA', {x: 0.1, y: 0.25});
CephApp.setManualDistancePoint('pointB', {x: 0.5, y: 0.25});
const distance = CephApp.addManualDistance('Airway AP');
return {
  calibrated,
  distance,
  snapshot: CephApp.getSnapshot(),
  scaleText: document.getElementById('scale-meta').textContent,
  distanceItems: document.querySelectorAll('#manual-distance-list li').length,
  addDisabled: document.getElementById('add-manual-distance').disabled
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertTrue(result["calibrated"]["ok"])
        self.assertAlmostEqual(
            result["snapshot"]["calibration"]["mmPerPixel"], 0.1
        )
        self.assertTrue(result["distance"]["ok"])
        self.assertAlmostEqual(result["distance"]["valueMm"], 20.0)
        self.assertEqual(result["distanceItems"], 1)
        self.assertFalse(result["addDisabled"])
        self.assertIn("0.1000", result["scaleText"])

    def test_skip_calibration_disables_linear_measurement(self) -> None:
        result = run_browser_probe(
            r"""
const sourceCanvas = document.createElement('canvas');
sourceCanvas.width = 500;
sourceCanvas.height = 200;
const blob = await new Promise(resolve => sourceCanvas.toBlob(resolve, 'image/png'));
await CephApp.loadImageFile(
  new File([blob], 'skip-ruler.png', { type: 'image/png' })
);
CephApp.goToStage('calibration');
const skipped = CephApp.skipCalibration();
return {
  skipped,
  snapshot: CephApp.getSnapshot(),
  addDisabled: document.getElementById('add-manual-distance').disabled,
  scaleText: document.getElementById('scale-meta').textContent
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertTrue(result["skipped"])
        self.assertTrue(result["snapshot"]["calibration"]["skipped"])
        self.assertIsNone(result["snapshot"]["calibration"]["mmPerPixel"])
        self.assertEqual(result["snapshot"]["currentStage"], "core")
        self.assertTrue(result["addDisabled"])
        self.assertIn("已跳過", result["scaleText"])


class CephCoreMeasurementTests(unittest.TestCase):
    def test_core_angle_fixture(self) -> None:
        result = run_core(
            """(() => {
              const rad = degrees => degrees * Math.PI / 180;
              const landmarks = {
                S: {x: 1, y: 0, uncertain: false},
                N: {x: 0, y: 0, uncertain: false},
                A: {x: Math.cos(rad(82)), y: Math.sin(rad(82)), uncertain: false},
                B: {x: Math.cos(rad(80)), y: Math.sin(rad(80)), uncertain: false}
              };
              return CephCore.computeMeasurements(landmarks);
            })()"""
        )

        self.assertAlmostEqual(result["measurements"]["SNA"]["value"], 82, places=2)
        self.assertAlmostEqual(result["measurements"]["SNB"]["value"], 80, places=2)
        self.assertAlmostEqual(result["measurements"]["ANB"]["value"], 2, places=2)
        self.assertEqual(result["missingCore"], [])

    def test_incomplete_core_omits_all_core_measurements(self) -> None:
        result = run_core(
            """CephCore.computeMeasurements({
              S: {x: 1, y: 0}, N: {x: 0, y: 0}, A: {x: 0.2, y: 0.8}
            })"""
        )

        self.assertEqual(result["measurements"], {})
        self.assertEqual(result["missingCore"], ["B"])
        self.assertIsNone(result["classification"])

    def test_anb_boundaries(self) -> None:
        result = run_core(
            """[-0.1, 0, 4, 4.1, null, '2'].map(CephCore.classifyANB)"""
        )

        self.assertEqual(
            result,
            [
                "Class III tendency",
                "Class I tendency",
                "Class I tendency",
                "Class II tendency",
                None,
                None,
            ],
        )

    def test_completed_core_updates_measurement_cards(self) -> None:
        result = run_browser_probe(
            r"""
const rad = degrees => degrees * Math.PI / 180;
CephApp.setLandmark('S', {x: 1, y: 0}, false);
CephApp.setLandmark('N', {x: 0, y: 0}, false);
CephApp.setLandmark('A', {x: Math.cos(rad(82)), y: Math.sin(rad(82))}, false);
CephApp.setLandmark('B', {x: Math.cos(rad(80)), y: Math.sin(rad(80))}, false);
return {
  measurements: CephApp.getSnapshot().measurements,
  sna: document.getElementById('result-sna').textContent,
  snb: document.getElementById('result-snb').textContent,
  anb: document.getElementById('result-anb').textContent
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertAlmostEqual(result["measurements"]["ANB"]["value"], 2, places=2)
        self.assertIn("82.0°", result["sna"])
        self.assertIn("80.0°", result["snb"])
        self.assertIn("2.0°", result["anb"])
        self.assertIn("Class I tendency", result["anb"])

    def test_advanced_dependencies(self) -> None:
        result = run_core(
            """CephCore.computeMeasurements({
              S: {x: 0.1, y: 0.1},
              N: {x: 0.9, y: 0.1},
              Go: {x: 0.2, y: 0.7},
              Me: {x: 0.8, y: 0.7}
            })"""
        )

        self.assertIn("SN-MP", result["measurements"])
        self.assertAlmostEqual(result["measurements"]["SN-MP"]["value"], 0)
        self.assertNotIn("PP-MP", result["measurements"])
        self.assertNotIn("U1-PP", result["measurements"])
        self.assertNotIn("L1-MP", result["measurements"])
        self.assertNotIn("Interincisal", result["measurements"])

    def test_dental_obtuse_convention(self) -> None:
        result = run_core(
            """(() => {
              const rad = degrees => degrees * Math.PI / 180;
              const pointAlong = (origin, degrees) => ({
                x: origin.x + 0.1 * Math.cos(rad(degrees)),
                y: origin.y + 0.1 * Math.sin(rad(degrees))
              });
              const uApex = {x: 0.4, y: 0.4};
              const lApex = {x: 0.6, y: 0.4};
              return CephCore.computeMeasurements({
                ANS: {x: 0.2, y: 0.2}, PNS: {x: 0.8, y: 0.2},
                Go: {x: 0.2, y: 0.8}, Me: {x: 0.8, y: 0.8},
                U1Apex: uApex, U1Tip: pointAlong(uApex, 70),
                L1Apex: lApex, L1Tip: pointAlong(lApex, 110)
              });
            })()"""
        )

        self.assertAlmostEqual(result["measurements"]["PP-MP"]["value"], 0)
        self.assertAlmostEqual(result["measurements"]["U1-PP"]["value"], 110)
        self.assertAlmostEqual(result["measurements"]["L1-MP"]["value"], 110)
        self.assertAlmostEqual(
            result["measurements"]["Interincisal"]["value"], 140
        )

    def test_uncertainty_propagation(self) -> None:
        result = run_core(
            """CephCore.computeMeasurements({
              S: {x: 0.1, y: 0.1, uncertain: true},
              N: {x: 0.9, y: 0.1, uncertain: false},
              Go: {x: 0.2, y: 0.7, uncertain: false},
              Me: {x: 0.8, y: 0.7, uncertain: false},
              ANS: {x: 0.2, y: 0.2, uncertain: false},
              PNS: {x: 0.8, y: 0.2, uncertain: false}
            })"""
        )

        self.assertTrue(result["measurements"]["SN-MP"]["uncertain"])
        self.assertFalse(result["measurements"]["PP-MP"]["uncertain"])

    def test_uncertainty_notice_appears_only_on_related_cards(self) -> None:
        result = run_browser_probe(
            r"""
CephApp.setLandmark('S', {x: 1, y: 0}, true);
CephApp.setLandmark('N', {x: 0, y: 0}, false);
CephApp.setLandmark('A', {x: 0.2, y: 0.8}, false);
CephApp.setLandmark('B', {x: 0.25, y: 0.75}, false);
CephApp.setLandmark('ANS', {x: 0.2, y: 0.2}, false);
CephApp.setLandmark('PNS', {x: 0.8, y: 0.2}, false);
CephApp.setLandmark('Go', {x: 0.2, y: 0.8}, false);
CephApp.setLandmark('Me', {x: 0.8, y: 0.8}, false);
return {
  sna: document.getElementById('result-sna').textContent,
  ppmp: document.getElementById('result-pp-mp').textContent
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertIn("需複核", result["sna"])
        self.assertNotIn("需複核", result["ppmp"])


class CephReportGenerationTests(unittest.TestCase):
    @staticmethod
    def _complete_state_expression(survey_expression: str) -> str:
        return f"""(() => {{
          const rad = degrees => degrees * Math.PI / 180;
          return {{
            survey: {survey_expression},
            calibration: {{distanceMm: 45, mmPerPixel: 0.1, skipped: false}},
            landmarks: {{
              S: {{x: 1, y: 0, uncertain: false}},
              N: {{x: 0, y: 0, uncertain: false}},
              A: {{x: Math.cos(rad(82)), y: Math.sin(rad(82)), uncertain: false}},
              B: {{x: Math.cos(rad(80)), y: Math.sin(rad(80)), uncertain: false}}
            }},
            manualDistances: [],
            optionalGroups: {{skeletal: true, dental: true}}
          }};
        }})()"""

    def test_report_sections(self) -> None:
        all_normal = """Object.fromEntries([
          'imageQuality', 'sellaSkullBase', 'sinusesNasopharynx',
          'tmj', 'jawsDentition', 'cervicalAirway'
        ].map(key => [key, {status: 'normal', note: ''}]))"""
        state = self._complete_state_expression(all_normal)
        report = run_core(f"CephCore.buildReport({state})")

        headings = [
            "Examination / Technique",
            "Findings",
            "Cephalometric Analysis",
            "Impression",
            "Limitations",
        ]
        positions = [report.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("SNA 82.0°", report)
        self.assertIn("SNB 80.0°", report)
        self.assertIn("ANB 2.0°", report)
        self.assertIn("Steiner adult reference", report)
        self.assertIn("Class I tendency", report)
        self.assertIn("not performed", report)

    def test_system_generated_report_is_english(self) -> None:
        all_normal = """Object.fromEntries([
          'imageQuality', 'sellaSkullBase', 'sinusesNasopharynx',
          'tmj', 'jawsDentition', 'cervicalAirway'
        ].map(key => [key, {status: 'normal', note: ''}]))"""
        state = self._complete_state_expression(all_normal)
        report = run_core(f"CephCore.buildReport({state})")

        self.assertIsNone(re.search(r"[\u3400-\u9fff]", report), report)
        self.assertIn("No additional significant abnormality", report)
        self.assertIn("not performed", report)

    def test_report_omits_unassessed_normality(self) -> None:
        unassessed = """Object.fromEntries([
          'imageQuality', 'sellaSkullBase', 'sinusesNasopharynx',
          'tmj', 'jawsDentition', 'cervicalAirway'
        ].map(key => [key, {status: 'unassessed', note: ''}]))"""
        state = self._complete_state_expression(unassessed)
        report = run_core(f"CephCore.buildReport({state})")

        self.assertIn("Not assessed", report)
        self.assertNotIn("No additional significant abnormality", report)

    def test_report_preserves_abnormal_note_verbatim(self) -> None:
        mixed = """({
          imageQuality: {status: 'normal', note: ''},
          sellaSkullBase: {status: 'normal', note: ''},
          sinusesNasopharynx: {status: 'abnormal', note: '右側上頷竇底黏膜增厚。'},
          tmj: {status: 'normal', note: ''},
          jawsDentition: {status: 'limited', note: '金屬重疊，評估受限。'},
          cervicalAirway: {status: 'unassessed', note: ''}
        })"""
        state = self._complete_state_expression(mixed)
        report = run_core(f"CephCore.buildReport({state})")

        self.assertIn("右側上頷竇底黏膜增厚。", report)
        self.assertIn("金屬重疊，評估受限。", report)
        without_notes = report.replace("右側上頷竇底黏膜增厚。", "").replace(
            "金屬重疊，評估受限。", ""
        )
        self.assertIsNone(re.search(r"[\u3400-\u9fff]", without_notes))
        self.assertIn("Paranasal sinuses / nasopharynx", report)
        self.assertIn("Jaws and visualized dentition", report)
        self.assertNotIn("No additional significant abnormality", report)

    def test_no_osa_diagnosis(self) -> None:
        for status in ("normal", "abnormal", "limited", "unassessed"):
            survey = f"""({{
              imageQuality: {{status: 'normal', note: ''}},
              sellaSkullBase: {{status: 'normal', note: ''}},
              sinusesNasopharynx: {{status: 'normal', note: ''}},
              tmj: {{status: 'normal', note: ''}},
              jawsDentition: {{status: 'normal', note: ''}},
              cervicalAirway: {{status: '{status}', note: ''}}
            }})"""
            state = self._complete_state_expression(survey)
            report = run_core(f"CephCore.buildReport({state})")
            lower = report.lower()
            self.assertIn("screening", lower)
            self.assertIn("obstructive sleep apnea", lower)
            self.assertNotIn("diagnostic of obstructive sleep apnea", lower)
            self.assertNotIn("no obstructive sleep apnea", lower)
            self.assertNotIn("obstructive sleep apnea is present", lower)

    def test_uncalibrated_report_has_no_pixel_derived_mm(self) -> None:
        report = run_core(
            """CephCore.buildReport({
              survey: {},
              calibration: {distanceMm: null, mmPerPixel: null, skipped: true},
              landmarks: {},
              manualDistances: [{label: 'Airway AP', valueMm: 20}],
              optionalGroups: {skeletal: true, dental: true}
            })"""
        )

        self.assertIn("No calibrated linear measurements were generated", report)
        self.assertNotIn("20.0 mm", report)


class CephReportSnapshotTests(unittest.TestCase):
    _CORE_SETUP = r"""
const rad = degrees => degrees * Math.PI / 180;
CephApp.setLandmark('S', {x: 1, y: 0}, false);
CephApp.setLandmark('N', {x: 0, y: 0}, false);
CephApp.setLandmark('A', {x: Math.cos(rad(82)), y: Math.sin(rad(82))}, false);
CephApp.setLandmark('B', {x: Math.cos(rad(80)), y: Math.sin(rad(80))}, false);
"""

    def test_report_snapshot_preserves_manual_edit(self) -> None:
        result = run_browser_probe(
            self._CORE_SETUP
            + r"""
CephApp.generateReport();
const output = document.getElementById('report-output');
output.value = '醫師人工修改內容。';
output.dispatchEvent(new Event('input', {bubbles: true}));
CephApp.setLandmark('A', {x: 0.25, y: 0.75}, false);
return {
  snapshot: CephApp.getSnapshot().report,
  output: output.value,
  staleHidden: document.getElementById('report-stale').hidden,
  buttonText: document.getElementById('generate-report').textContent
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertEqual(result["snapshot"]["text"], "醫師人工修改內容。")
        self.assertEqual(result["output"], "醫師人工修改內容。")
        self.assertTrue(result["snapshot"]["stale"])
        self.assertFalse(result["staleHidden"])
        self.assertIn("重新產生", result["buttonText"])

    def test_explicit_regeneration_requires_confirmation(self) -> None:
        result = run_browser_probe(
            self._CORE_SETUP
            + r"""
CephApp.generateReport();
CephApp.setReportText('保留這段人工文字。');
CephApp.setLandmark('A', {x: 0.25, y: 0.75}, false);
globalThis.confirm = () => false;
const cancelled = CephApp.generateReport();
const afterCancel = CephApp.getSnapshot().report;
globalThis.confirm = () => true;
const regenerated = CephApp.generateReport();
return {
  cancelled,
  afterCancel,
  regenerated,
  finalReport: CephApp.getSnapshot().report,
  output: document.getElementById('report-output').value
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertEqual(result["cancelled"]["code"], "regeneration-cancelled")
        self.assertEqual(result["afterCancel"]["text"], "保留這段人工文字。")
        self.assertTrue(result["afterCancel"]["stale"])
        self.assertTrue(result["regenerated"]["ok"])
        self.assertFalse(result["finalReport"]["stale"])
        self.assertNotEqual(result["output"], "保留這段人工文字。")

    def test_copy_fallback_preserves_selectable_text(self) -> None:
        result = run_browser_probe(
            self._CORE_SETUP
            + r"""
CephApp.generateReport();
document.getElementById('report-panel').hidden = false;
let copied = '';
Object.defineProperty(navigator, 'clipboard', {
  configurable: true,
  value: {writeText: async text => { copied = text; }}
});
const success = await CephApp.copyReport();
Object.defineProperty(navigator, 'clipboard', {
  configurable: true,
  value: {writeText: async () => { throw new Error('blocked'); }}
});
const fallback = await CephApp.copyReport();
const output = document.getElementById('report-output');
return {
  success,
  fallback,
  copiedMatches: copied === output.value,
  reportMatches: CephApp.getSnapshot().report.text === output.value,
  activeId: document.activeElement.id,
  status: document.getElementById('aria-status').textContent
};
"""
        )

        self.assertNotIn("__error", result)
        self.assertTrue(result["success"]["ok"])
        self.assertFalse(result["fallback"]["ok"])
        self.assertTrue(result["copiedMatches"])
        self.assertTrue(result["reportMatches"])
        self.assertEqual(result["activeId"], "report-output")
        self.assertIn("手動", result["status"])


if __name__ == "__main__":
    unittest.main()
