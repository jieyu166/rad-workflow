from __future__ import annotations

import html
import json
import re
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


HTML_PATH = Path(__file__).parents[1] / "tool" / "image-stack-mpr.html"


class ImageStackPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: dict[str, dict[str, str | None]] = {}
        self.external_assets: list[tuple[str, str]] = []
        self.core_script: list[str] = []
        self.app_script: list[str] = []
        self._in_core_script = False
        self._in_app_script = False

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            self.elements[element_id] = attributes
        if tag == "script" and element_id == "image-stack-mpr-core":
            self._in_core_script = True
        elif tag == "script" and not attributes.get("src"):
            self._in_app_script = True
        for attribute in ("src", "href"):
            value = attributes.get(attribute)
            if value:
                self.external_assets.append((attribute, value))

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_core_script:
            self._in_core_script = False
        elif tag == "script" and self._in_app_script:
            self._in_app_script = False

    def handle_data(self, data: str) -> None:
        if self._in_core_script:
            self.core_script.append(data)
        elif self._in_app_script:
            self.app_script.append(data)


def parse_page() -> tuple[str, ImageStackPageParser]:
    source = HTML_PATH.read_text(encoding="utf-8")
    parser = ImageStackPageParser()
    parser.feed(source)
    return source, parser


def run_core(expression: str):
    _, parser = parse_page()
    source = "".join(parser.core_script)
    if not source.strip():
        raise AssertionError("image-stack-mpr-core script is missing")
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


def measure_full_width_layout() -> dict[str, float | int]:
    browser_candidates = (
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    )
    browser = next((path for path in browser_candidates if path.exists()), None)
    if browser is None:
        raise unittest.SkipTest("Chrome or Edge is required for layout verification")

    source, _ = parse_page()
    probe = r"""
<script>
(() => {
  const boundaryHost = document.getElementById("boundary-controls");
  boundaryHost.innerHTML = [1, 2].map(index => [
    '<label class="boundary-row">',
    `<span>Boundary ${index}</span>`,
    '<input type="range" min="1" max="99" value="50">',
    '<output>50</output>',
    '</label>'
  ].join('')).join('');

  const lanes = document.getElementById("sequence-lanes");
  lanes.innerHTML = '<section class="sequence-lane">' +
    '<div class="lane-title">Sequence 1</div>' +
    '<div class="thumbnail-strip"></div></section>';
  const timeline = lanes.querySelector('.thumbnail-strip');
  for (let index = 0; index < 100; index += 1) {
    const card = document.createElement('article');
    card.className = 'thumbnail-card';
    card.textContent = String(index + 1);
    timeline.appendChild(card);
  }

  const sidebarBox = document.querySelector('.sidebar').getBoundingClientRect();
  const mainBox = document.querySelector('.main').getBoundingClientRect();
  const boundaryBox = boundaryHost.querySelector('.boundary-row')
    .getBoundingClientRect();
  const sliderBox = boundaryHost.querySelector('input[type="range"]')
    .getBoundingClientRect();
  const thumbnailRows = new Set(
    Array.from(timeline.children, card => Math.round(card.getBoundingClientRect().top))
  ).size;
  const result = {
    viewportWidth: document.documentElement.clientWidth,
    sidebarBottom: sidebarBox.bottom,
    sidebarWidth: sidebarBox.width,
    mainTop: mainBox.top,
    mainWidth: mainBox.width,
    boundaryRight: boundaryBox.right,
    sliderRight: sliderBox.right,
    thumbnailRows,
    timelineClientWidth: timeline.clientWidth,
    timelineScrollWidth: timeline.scrollWidth
  };
  document.body.innerHTML = '<pre id="layout-result">' +
    JSON.stringify(result) + '</pre>';
})();
</script>
"""
    fixture = source.replace("</body>", probe + "</body>")
    with tempfile.TemporaryDirectory() as temp_dir:
        fixture_path = Path(temp_dir) / "full-width-layout.html"
        fixture_path.write_text(fixture, encoding="utf-8")
        completed = subprocess.run(
            [
                str(browser),
                "--headless=new",
                "--disable-gpu",
                "--disable-extensions",
                "--no-first-run",
                f"--user-data-dir={Path(temp_dir) / 'profile'}",
                "--window-size=1200,800",
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
        r'<pre id="layout-result">(\{.*?\})</pre>', completed.stdout
    )
    if match is None:
        raise AssertionError("Browser did not return full-width layout measurements")
    return json.loads(html.unescape(match.group(1)))


def render_crosslink_filename_probe() -> dict[str, bool | str]:
    browser_candidates = (
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    )
    browser = next((path for path in browser_candidates if path.exists()), None)
    if browser is None:
        raise unittest.SkipTest("Chrome or Edge is required for UI verification")

    source, _ = parse_page()
    app_end = """    renderOrganizer();
  }());
  </script>"""
    instrumented_end = """    renderOrganizer();
    globalThis.__filenameTest = {
      state,
      createViewport,
      updateViewportFilename: typeof updateViewportFilename === "function"
        ? updateViewportFilename
        : null
    };
  }());
  </script>"""
    if app_end not in source:
        raise AssertionError("Unable to instrument the viewer app script")
    source = source.replace(app_end, instrumented_end, 1)
    probe = r"""
<script>
(() => {
  const api = globalThis.__filenameTest;
  api.state.volumes.set(1, {
    id: 1,
    depth: 3,
    sliceNames: ['0001.jpg', '0002.jpg', '0003.jpg']
  });
  api.state.positions[1] = 1;
  const crosslinkRoot = api.createViewport(1, 'AX', 'filename-crosslink', true);
  const mprRoot = api.createViewport(1, 'AX', 'filename-mpr', false);
  document.body.replaceChildren(crosslinkRoot, mprRoot);
  const crosslinkViewport = api.state.viewports.get('filename-crosslink');
  if (api.updateViewportFilename) api.updateViewportFilename(crosslinkViewport);
  const footer = crosslinkRoot.querySelector('.viewport-filename');
  const card = crosslinkViewport.card;
  const result = {
    crosslinkText: footer ? footer.textContent : '',
    crosslinkTitle: footer ? footer.title : '',
    footerBelowCard: footer
      ? footer.getBoundingClientRect().top >= card.getBoundingClientRect().bottom
      : false,
    mprHasFilename: Boolean(mprRoot.querySelector('.viewport-filename'))
  };
  document.body.innerHTML = '<pre id="filename-result">' +
    JSON.stringify(result) + '</pre>';
})();
</script>
"""
    fixture = source.replace("</body>", probe + "</body>")
    with tempfile.TemporaryDirectory() as temp_dir:
        fixture_path = Path(temp_dir) / "crosslink-filename.html"
        fixture_path.write_text(fixture, encoding="utf-8")
        completed = subprocess.run(
            [
                str(browser),
                "--headless=new",
                "--disable-gpu",
                "--disable-extensions",
                "--no-first-run",
                f"--user-data-dir={Path(temp_dir) / 'profile'}",
                "--window-size=1200,800",
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
        r'<pre id="filename-result">(\{.*?\})</pre>', completed.stdout
    )
    if match is None:
        raise AssertionError("Browser did not return filename UI measurements")
    return json.loads(html.unescape(match.group(1)))


def run_crosslink_interaction_probe() -> dict[str, object]:
    browser_candidates = (
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    )
    browser = next((path for path in browser_candidates if path.exists()), None)
    if browser is None:
        raise unittest.SkipTest("Chrome or Edge is required for UI verification")

    source, _ = parse_page()
    app_end = """    renderOrganizer();
  }());
  </script>"""
    instrumented_end = """    renderOrganizer();
    globalThis.__interactionTest = {state, createViewport};
  }());
  </script>"""
    if app_end not in source:
        raise AssertionError("Unable to instrument the viewer app script")
    source = source.replace(app_end, instrumented_end, 1)
    probe = r"""
<script>
(() => {
  const api = globalThis.__interactionTest;
  const host = document.getElementById('axial-viewports');
  host.replaceChildren();
  [1, 2, 3].forEach(sequenceId => {
    host.appendChild(api.createViewport(
      sequenceId, 'AX', `cross-${sequenceId}-ax`, true
    ));
  });
  const sync = document.getElementById('sync-navigation');
  const canvas = api.state.viewports.get('cross-2-ax').canvas;
  const zooms = () => Object.fromEntries([1, 2, 3].map(sequenceId => [
    sequenceId,
    api.state.viewportStates.get(`cross-${sequenceId}-ax`).zoom
  ]));
  const resetZooms = () => [1, 2, 3].forEach(sequenceId => {
    api.state.viewportStates.get(`cross-${sequenceId}-ax`).zoom = 1;
  });

  canvas.dispatchEvent(new PointerEvent('pointerenter'));
  globalThis.dispatchEvent(new KeyboardEvent('keydown', {
    key: '+', code: 'Equal', bubbles: true, cancelable: true
  }));
  const syncedPlus = zooms();

  resetZooms();
  sync.checked = false;
  globalThis.dispatchEvent(new KeyboardEvent('keydown', {
    key: '-', code: 'NumpadSubtract', bubbles: true, cancelable: true
  }));
  const unsyncedMinus = zooms();

  canvas.dispatchEvent(new PointerEvent('pointerleave'));
  const beforeNoHover = zooms();
  globalThis.dispatchEvent(new KeyboardEvent('keydown', {
    key: '+', code: 'NumpadAdd', bubbles: true, cancelable: true
  }));
  const noHover = zooms();

  resetZooms();
  canvas.dispatchEvent(new PointerEvent('pointerenter'));
  const wheelStart = api.state.viewportStates.get('cross-2-ax').zoom;
  canvas.dispatchEvent(new WheelEvent('wheel', {
    deltaY: 100, ctrlKey: true, bubbles: true, cancelable: true
  }));
  const wheelDown = api.state.viewportStates.get('cross-2-ax').zoom;
  canvas.dispatchEvent(new WheelEvent('wheel', {
    deltaY: -100, ctrlKey: true, bubbles: true, cancelable: true
  }));
  const wheelUp = api.state.viewportStates.get('cross-2-ax').zoom;

  const result = {
    syncedPlus,
    unsyncedMinus,
    beforeNoHover,
    noHover,
    wheelStart,
    wheelDown,
    wheelUp
  };
  document.body.innerHTML = '<pre id="interaction-result">' +
    JSON.stringify(result) + '</pre>';
})();
</script>
"""
    fixture = source.replace("</body>", probe + "</body>")
    with tempfile.TemporaryDirectory() as temp_dir:
        fixture_path = Path(temp_dir) / "crosslink-interactions.html"
        fixture_path.write_text(fixture, encoding="utf-8")
        completed = subprocess.run(
            [
                str(browser),
                "--headless=new",
                "--disable-gpu",
                "--disable-extensions",
                "--no-first-run",
                f"--user-data-dir={Path(temp_dir) / 'profile'}",
                "--window-size=1200,800",
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
        r'<pre id="interaction-result">(\{.*?\})</pre>', completed.stdout
    )
    if match is None:
        raise AssertionError("Browser did not return interaction measurements")
    return json.loads(html.unescape(match.group(1)))


def measure_crosslink_orientation_layout() -> dict[str, object]:
    browser_candidates = (
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    )
    browser = next((path for path in browser_candidates if path.exists()), None)
    if browser is None:
        raise unittest.SkipTest("Chrome or Edge is required for layout verification")

    source, _ = parse_page()
    app_end = """    renderOrganizer();
  }());
  </script>"""
    instrumented_end = """    renderOrganizer();
    globalThis.__orientationTest = {state, createViewport};
  }());
  </script>"""
    if app_end not in source:
        raise AssertionError("Unable to instrument the viewer app script")
    source = source.replace(app_end, instrumented_end, 1)
    probe = r"""
<script>
(() => {
  const api = globalThis.__orientationTest;
  const host = document.getElementById('axial-viewports');
  host.className = 'viewport-grid';
  host.replaceChildren();
  [1, 2, 3].forEach(sequenceId => {
    host.appendChild(api.createViewport(
      sequenceId, 'AX', `orientation-${sequenceId}`, true
    ));
  });
  const hostBox = host.getBoundingClientRect();
  const boxes = Array.from(host.children, child => child.getBoundingClientRect());
  const result = {
    portrait: matchMedia('(orientation: portrait)').matches,
    rows: new Set(boxes.map(box => Math.round(box.top))).size,
    fullWidth: boxes.map(box => Math.abs(box.width - hostBox.width) <= 2)
  };
  document.body.innerHTML = '<pre id="orientation-result">' +
    JSON.stringify(result) + '</pre>';
})();
</script>
"""
    fixture = source.replace("</body>", probe + "</body>")

    def measure(window_size: str) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_path = Path(temp_dir) / "crosslink-orientation.html"
            fixture_path.write_text(fixture, encoding="utf-8")
            completed = subprocess.run(
                [
                    str(browser),
                    "--headless=new",
                    "--disable-gpu",
                    "--disable-extensions",
                    "--no-first-run",
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
            r'<pre id="orientation-result">(\{.*?\})</pre>', completed.stdout
        )
        if match is None:
            raise AssertionError("Browser did not return orientation measurements")
        return json.loads(html.unescape(match.group(1)))

    portrait = measure("700,1100")
    landscape = measure("1200,700")
    return {
        "portraitMedia": portrait["portrait"],
        "portraitRows": portrait["rows"],
        "portraitFullWidth": portrait["fullWidth"],
        "landscapeMedia": landscape["portrait"],
        "landscapeRows": landscape["rows"],
    }


def run_batch_anchor_ui_probe() -> dict[str, object]:
    browser_candidates = (
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    )
    browser = next((path for path in browser_candidates if path.exists()), None)
    if browser is None:
        raise unittest.SkipTest("Chrome or Edge is required for UI verification")

    source, _ = parse_page()
    app_end = """    renderOrganizer();
  }());
  </script>"""
    instrumented_end = """    renderOrganizer();
    globalThis.__batchAnchorTest = {state};
  }());
  </script>"""
    if app_end not in source:
        raise AssertionError("Unable to instrument the viewer app script")
    source = source.replace(app_end, instrumented_end, 1)
    probe = r"""
<script>
(() => {
  const api = globalThis.__batchAnchorTest;
  const sequenceCount = document.getElementById('sequence-count');
  const addButton = document.getElementById('add-anchor');
  const message = document.getElementById('anchor-message');
  const snapshot = () => JSON.parse(JSON.stringify(api.state.crosslinks));

  sequenceCount.value = '3';
  api.state.crosslinks = ImageStackMprCore.createCrosslinkMaps(3);
  api.state.positions = {1: 24, 2: 27, 3: 26};
  addButton.click();
  const successMaps = snapshot();
  const successMessage = message.textContent;

  const beforeRejected = snapshot();
  api.state.positions = {1: 24, 2: 31, 3: 32};
  addButton.click();
  const afterRejected = snapshot();
  const failureMessage = message.textContent;

  sequenceCount.value = '2';
  api.state.crosslinks = ImageStackMprCore.createCrosslinkMaps(2);
  api.state.positions = {1: 4, 2: 8};
  addButton.click();
  const twoSequenceMaps = snapshot();

  const result = {
    successMaps,
    successMessage,
    beforeRejected,
    afterRejected,
    failureMessage,
    twoSequenceMaps
  };
  document.body.innerHTML = '<pre id="batch-anchor-result">' +
    JSON.stringify(result) + '</pre>';
})();
</script>
"""
    fixture = source.replace("</body>", probe + "</body>")
    with tempfile.TemporaryDirectory() as temp_dir:
        fixture_path = Path(temp_dir) / "batch-anchor-ui.html"
        fixture_path.write_text(fixture, encoding="utf-8")
        completed = subprocess.run(
            [
                str(browser),
                "--headless=new",
                "--disable-gpu",
                "--disable-extensions",
                "--no-first-run",
                f"--user-data-dir={Path(temp_dir) / 'profile'}",
                "--window-size=1200,800",
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
        r'<pre id="batch-anchor-result">(\{.*?\})</pre>', completed.stdout
    )
    if match is None:
        raise AssertionError("Browser did not return batch-anchor results")
    return json.loads(html.unescape(match.group(1)))


class ImageStackMprTests(unittest.TestCase):
    def test_canonical_slice_filename_mapping(self) -> None:
        result = run_core(
            r"""
(() => {
  const available = typeof ImageStackMprCore.canonicalSliceNames === "function"
    && typeof ImageStackMprCore.sliceNameAtPosition === "function";
  if (!available) return {available};
  const items = [
    {name: "0001.jpg", width: 8, height: 6},
    {name: "0002.jpg", width: 8, height: 6},
    {name: "0003.jpg", width: 8, height: 6}
  ];
  const forward = ImageStackMprCore.canonicalSliceNames(
    items, ImageStackMprCore.normalizeGeometry({order: "forward"})
  );
  const reverse = ImageStackMprCore.canonicalSliceNames(
    items, ImageStackMprCore.normalizeGeometry({order: "reverse"})
  );
  return {
    available,
    forward,
    reverse,
    fractional: ImageStackMprCore.sliceNameAtPosition(forward, 1.4),
    roundedUp: ImageStackMprCore.sliceNameAtPosition(forward, 1.6),
    clamped: ImageStackMprCore.sliceNameAtPosition(forward, 99)
  };
})()
"""
        )

        self.assertTrue(result["available"])
        self.assertEqual(result["forward"], ["0001.jpg", "0002.jpg", "0003.jpg"])
        self.assertEqual(result["reverse"], ["0003.jpg", "0002.jpg", "0001.jpg"])
        self.assertEqual(result["fractional"], "0002.jpg")
        self.assertEqual(result["roundedUp"], "0003.jpg")
        self.assertEqual(result["clamped"], "0003.jpg")

    def test_crosslink_viewport_displays_current_filename_below_image(self) -> None:
        result = render_crosslink_filename_probe()

        self.assertEqual(result["crosslinkText"], "檔案：0002.jpg")
        self.assertEqual(result["crosslinkTitle"], "0002.jpg")
        self.assertTrue(result["footerBelowCard"])
        self.assertFalse(result["mprHasFilename"])

    def test_setup_and_sequence_timeline_use_full_width_vertical_flow(self) -> None:
        layout = measure_full_width_layout()

        self.assertGreaterEqual(layout["mainTop"], layout["sidebarBottom"] - 1)
        self.assertAlmostEqual(
            layout["sidebarWidth"], layout["mainWidth"], delta=2
        )
        self.assertLessEqual(layout["sidebarWidth"], layout["viewportWidth"] + 0.5)
        self.assertLessEqual(layout["mainWidth"], layout["viewportWidth"] + 0.5)
        self.assertLessEqual(
            layout["sliderRight"], layout["boundaryRight"] + 0.5
        )
        self.assertEqual(layout["thumbnailRows"], 1)
        self.assertGreater(
            layout["timelineScrollWidth"], layout["timelineClientWidth"]
        )

    def test_offline_single_file_image_stack_import(self) -> None:
        source, parser = parse_page()
        required_ids = {
            "image-file-input",
            "sequence-count",
            "organizer",
            "crosslink-workspace",
            "mpr-workspace",
        }

        self.assertTrue(required_ids.issubset(parser.elements))
        self.assertIn("accept=\".png,.jpg,.jpeg,image/png,image/jpeg\"", source)
        self.assertFalse(parser.external_assets)
        self.assertIsNone(re.search(r"(?:https?:)?//", source, re.IGNORECASE))
        self.assertIsNone(re.search(r"url\s*\(\s*['\"]?(?!data:|blob:)", source))

    def test_core_script_is_extractable_and_executable(self) -> None:
        result = run_core(
            "Object.keys(ImageStackMprCore).sort()"
        )

        self.assertIn("naturalCompare", result)
        self.assertIn("sampleTrilinear", result)
        self.assertIn("reslicePlane", result)

    def test_browser_script_has_valid_syntax(self) -> None:
        _, parser = parse_page()
        source = "".join(parser.app_script)

        self.assertTrue(source.strip())
        subprocess.run(
            [
                "node",
                "-e",
                'const fs=require("node:fs");new Function(fs.readFileSync(0,"utf8"));',
            ],
            input=source,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_natural_ordering_and_sequence_count(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const names = ["IMG_10.png", "img_2.png", "IMG_1.png"]
    .sort(C.naturalCompare);
  const sixtySix = Array.from({length: 66}, (_, index) => ({
    id: `f${index + 1}`,
    name: `IMG_${index + 1}.png`
  }));
  const two = C.assignByBoundaries(sixtySix, 2, [30]);
  const three = C.assignByBoundaries(sixtySix.slice(0, 6), 3, [2, 4]);
  let rejected = false;
  try { C.assignByBoundaries(sixtySix, 4, [20, 40, 60]); }
  catch (error) { rejected = true; }
  return {
    names,
    firstSequence: two.slice(0, 30).map(item => item.sequenceId),
    secondSequence: two.slice(30).map(item => item.sequenceId),
    three: three.map(item => item.sequenceId),
    rejected
  };
})()
"""
        )

        self.assertEqual(result["names"], ["IMG_1.png", "img_2.png", "IMG_10.png"])
        self.assertEqual(result["firstSequence"], [1] * 30)
        self.assertEqual(result["secondSequence"], [2] * 36)
        self.assertEqual(result["three"], [1, 1, 2, 2, 3, 3])
        self.assertTrue(result["rejected"])

    def test_boundary_and_per_image_assignment(self) -> None:
        source, parser = parse_page()
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const original = C.assignByBoundaries([
    {id: "a", name: "IMG_1.png"},
    {id: "b", name: "IMG_2.png"},
    {id: "c", name: "IMG_3.png"}
  ], 2, [1]);
  const moved = C.reassignItem(original, "b", 1, 2);
  const excluded = C.setItemIncluded(moved, "c", false);
  return {
    original: original.map(item => [item.id, item.sequenceId, item.included]),
    changed: excluded.map(item => [item.id, item.sequenceId, item.included]),
    stableNames: excluded.map(item => item.name)
  };
})()
"""
        )

        self.assertEqual(
            result["original"],
            [["a", 1, True], ["b", 2, True], ["c", 2, True]],
        )
        self.assertEqual(
            result["changed"],
            [["a", 1, True], ["b", 1, True], ["c", 2, False]],
        )
        self.assertEqual(result["stableNames"], ["IMG_1.png", "IMG_2.png", "IMG_3.png"])
        self.assertIn("sequence-lanes", parser.elements)
        self.assertIn("boundary-controls", parser.elements)
        self.assertIn("build-volumes", parser.elements)
        self.assertIn("draggable", source)

    def test_sequence_geometry_configuration(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const defaults = C.normalizeGeometry({});
  const valid = C.normalizeGeometry({
    pixelSpacingX: 0.7,
    pixelSpacingY: 0.8,
    sliceSpacing: 3,
    order: "reverse",
    rotation: 90,
    flipX: true,
    flipY: false
  });
  const invalid = C.normalizeGeometry({
    pixelSpacingX: 0,
    pixelSpacingY: -1,
    sliceSpacing: "bad",
    order: "sideways",
    rotation: 45
  });
  return {
    defaults,
    valid,
    invalid,
    dims90: C.canonicalDimensions(3, 2, 4, valid),
    map90: C.canonicalToSource(0, 0, 0, 3, 2, 4, valid),
    map270: C.canonicalToSource(
      1, 2, 3, 3, 2, 4,
      C.normalizeGeometry({rotation: 270})
    )
  };
})()
"""
        )

        self.assertEqual(
            result["defaults"],
            {
                "orientation": "axial",
                "pixelSpacingX": 1,
                "pixelSpacingY": 1,
                "sliceSpacing": 5,
                "order": "forward",
                "rotation": 0,
                "flipX": False,
                "flipY": False,
                "unknownScale": True,
            },
        )
        self.assertFalse(result["valid"]["unknownScale"])
        self.assertEqual(result["invalid"]["pixelSpacingX"], 1)
        self.assertEqual(result["invalid"]["pixelSpacingY"], 1)
        self.assertEqual(result["invalid"]["sliceSpacing"], 5)
        self.assertTrue(result["invalid"]["unknownScale"])
        self.assertEqual(result["dims90"], {"width": 2, "height": 3, "depth": 4})
        self.assertEqual(result["map90"], {"x": 0, "y": 0, "z": 3})
        self.assertEqual(result["map270"], {"x": 0, "y": 1, "z": 3})

    def test_decode_and_dimension_validation(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const geometry = C.normalizeGeometry({rotation: 90});
  const valid = C.validateDecodedSequence([
    {name: "a.png", width: 3, height: 2, ok: true},
    {name: "b.jpg", width: 3, height: 2, ok: true}
  ], geometry);
  const mismatch = C.validateDecodedSequence([
    {name: "a.png", width: 3, height: 2, ok: true},
    {name: "bad.png", width: 4, height: 2, ok: true}
  ], geometry);
  const failed = C.validateDecodedSequence([
    {name: "broken.jpg", ok: false, error: "decode"},
    {name: "b.jpg", width: 3, height: 2, ok: true}
  ], geometry);
  const shallow = C.validateDecodedSequence([
    {name: "only.png", width: 3, height: 2, ok: true}
  ], geometry);
  return {valid, mismatch, failed, shallow};
})()
"""
        )

        self.assertTrue(result["valid"]["valid"])
        self.assertEqual(result["valid"]["width"], 2)
        self.assertEqual(result["valid"]["height"], 3)
        self.assertEqual(result["valid"]["depth"], 2)
        self.assertFalse(result["mismatch"]["valid"])
        self.assertIn("bad.png", result["mismatch"]["errors"][0])
        self.assertFalse(result["failed"]["valid"])
        self.assertIn("broken.jpg", result["failed"]["errors"][0])
        self.assertFalse(result["shallow"]["valid"])
        self.assertIn("至少 2 張", result["shallow"]["errors"][0])

    def test_memory_aware_volume_construction(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const below = C.estimateVolumeBytes([{width: 512, height: 512, depth: 2047}]);
  const atLimit = C.estimateVolumeBytes([{width: 512, height: 512, depth: 2048}]);
  const allocation = C.allocateVolume(
    {sequenceId: 2, width: 8, height: 8, depth: 8},
    () => { throw new Error("allocation denied"); }
  );
  return {
    below,
    atLimit,
    belowNeedsConfirmation: C.requiresMemoryConfirmation(below),
    limitNeedsConfirmation: C.requiresMemoryConfirmation(atLimit),
    allocation
  };
})()
"""
        )

        self.assertEqual(result["atLimit"], 512 * 1024 * 1024)
        self.assertFalse(result["belowNeedsConfirmation"])
        self.assertTrue(result["limitNeedsConfirmation"])
        self.assertFalse(result["allocation"]["ok"])
        self.assertEqual(result["allocation"]["sequenceId"], 2)
        self.assertIn("allocation denied", result["allocation"]["error"])

    def test_reference_based_crosslink_model(self) -> None:
        result = run_core(
            r"""
(() => {
  const maps = ImageStackMprCore.createCrosslinkMaps(3);
  maps[2].push({referenceIndex: 16, targetIndex: 50});
  maps[3].push({referenceIndex: 8, targetIndex: 20});
  return maps;
})()
"""
        )

        self.assertEqual(result["2"], [{"referenceIndex": 16, "targetIndex": 50}])
        self.assertEqual(result["3"], [{"referenceIndex": 8, "targetIndex": 20}])

    def test_strictly_monotonic_anchor_validation(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const anchors = [
    {referenceIndex: 7, targetIndex: 39},
    {referenceIndex: 27, targetIndex: 63}
  ];
  return {
    valid: C.validateAnchor({referenceIndex: 17, targetIndex: 51}, anchors),
    crossing: C.validateAnchor({referenceIndex: 20, targetIndex: 65}, anchors),
    duplicateReference: C.validateAnchor({referenceIndex: 7, targetIndex: 40}, anchors),
    duplicateTarget: C.validateAnchor({referenceIndex: 8, targetIndex: 39}, anchors),
    unchanged: anchors
  };
})()
"""
        )

        self.assertTrue(result["valid"]["valid"])
        self.assertFalse(result["crossing"]["valid"])
        self.assertIn("單調", result["crossing"]["reason"])
        self.assertFalse(result["duplicateReference"]["valid"])
        self.assertIn("reference", result["duplicateReference"]["reason"])
        self.assertFalse(result["duplicateTarget"]["valid"])
        self.assertIn("target", result["duplicateTarget"]["reason"])
        self.assertEqual(
            result["unchanged"],
            [
                {"referenceIndex": 7, "targetIndex": 39},
                {"referenceIndex": 27, "targetIndex": 63},
            ],
        )

    def test_piecewise_mapping_behavior(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const pair = [
    {referenceIndex: 7, targetIndex: 39},
    {referenceIndex: 27, targetIndex: 63}
  ];
  return {
    none: C.mapReferenceToTarget(18, [], 100),
    one: C.mapReferenceToTarget(18, [{referenceIndex: 16, targetIndex: 50}], 100),
    middle: C.mapReferenceToTarget(17, pair, 100),
    before: C.mapReferenceToTarget(-100, pair, 100),
    after: C.mapReferenceToTarget(200, pair, 70),
    inverse: C.mapTargetToReference(51, pair, 100)
  };
})()
"""
        )

        self.assertIsNone(result["none"])
        self.assertEqual(result["one"], 52)
        self.assertEqual(result["middle"], 51)
        self.assertEqual(result["before"], 0)
        self.assertEqual(result["after"], 69)
        self.assertEqual(result["inverse"], 17)

    def test_reversible_synchronization(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const maps = C.createCrosslinkMaps(3);
  maps[2] = [
    {referenceIndex: 7, targetIndex: 39},
    {referenceIndex: 27, targetIndex: 63}
  ];
  maps[3] = [
    {referenceIndex: 7, targetIndex: 19},
    {referenceIndex: 27, targetIndex: 43}
  ];
  return {
    fromReference: C.synchronizePositions(1, 16.5, maps, {1: 80, 2: 90, 3: 70}, {1: 0, 2: 0, 3: 0}),
    fromSecondary: C.synchronizePositions(2, 51, maps, {1: 80, 2: 90, 3: 70}, {1: 0, 2: 0, 3: 0}),
    independent: C.synchronizePositions(1, 25, C.createCrosslinkMaps(2), {1: 80, 2: 90}, {1: 4, 2: 44})
  };
})()
"""
        )

        self.assertAlmostEqual(result["fromReference"]["2"], 50.4)
        self.assertAlmostEqual(result["fromReference"]["3"], 30.4)
        self.assertEqual(result["fromSecondary"], {"1": 17, "2": 51, "3": 31})
        self.assertEqual(result["independent"], {"1": 25, "2": 44})

    def test_anchor_creation_and_editing(self) -> None:
        source, parser = parse_page()
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const added = C.upsertAnchor([], {referenceIndex: 16, targetIndex: 50});
  const updated = C.upsertAnchor(added.anchors, {referenceIndex: 17, targetIndex: 51}, 0);
  const rejected = C.upsertAnchor(updated.anchors, {referenceIndex: 17, targetIndex: 60});
  const deleted = C.deleteAnchor(updated.anchors, 0);
  return {added, updated, rejected, deleted};
})()
"""
        )

        self.assertTrue(result["added"]["valid"])
        self.assertEqual(result["added"]["anchors"], [{"referenceIndex": 16, "targetIndex": 50}])
        self.assertEqual(result["updated"]["anchors"], [{"referenceIndex": 17, "targetIndex": 51}])
        self.assertFalse(result["rejected"]["valid"])
        self.assertEqual(result["rejected"]["anchors"], result["updated"]["anchors"])
        self.assertEqual(result["deleted"], [])
        for element_id in ("anchor-target", "add-anchor", "update-anchor", "delete-anchor"):
            self.assertIn(element_id, parser.elements)
        self.assertIn("目前切片", source)

    def test_batch_anchor_creation_is_atomic(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  if (typeof C.batchUpsertAnchors !== 'function') return {available: false};
  const maps = {
    2: [{referenceIndex: 5, targetIndex: 8}],
    3: [{referenceIndex: 5, targetIndex: 6}]
  };
  return {
    available: true,
    success: C.batchUpsertAnchors(maps, {
      2: {referenceIndex: 10, targetIndex: 14},
      3: {referenceIndex: 10, targetIndex: 12}
    }),
    rejected: C.batchUpsertAnchors(maps, {
      2: {referenceIndex: 10, targetIndex: 14},
      3: {referenceIndex: 5, targetIndex: 12}
    }),
    twoSequence: C.batchUpsertAnchors({2: []}, {
      2: {referenceIndex: 4, targetIndex: 8}
    }),
    original: maps
  };
})()
"""
        )

        self.assertTrue(result["available"])
        self.assertTrue(result["success"]["valid"])
        self.assertEqual(len(result["success"]["maps"]["2"]), 2)
        self.assertEqual(len(result["success"]["maps"]["3"]), 2)
        self.assertFalse(result["rejected"]["valid"])
        self.assertEqual(result["rejected"]["failedTargetId"], 3)
        self.assertEqual(result["rejected"]["maps"], result["original"])
        self.assertEqual(result["original"]["2"], [
            {"referenceIndex": 5, "targetIndex": 8}
        ])
        self.assertTrue(result["twoSequence"]["valid"])
        self.assertEqual(list(result["twoSequence"]["maps"]), ["2"])

    def test_batch_anchor_button_updates_all_active_sequences(self) -> None:
        source, _ = parse_page()
        result = run_batch_anchor_ui_probe()

        self.assertIn("新增全部序列錨點", source)
        self.assertIn("編輯目標", source)
        self.assertEqual(len(result["successMaps"]["2"]), 1)
        self.assertEqual(len(result["successMaps"]["3"]), 1)
        self.assertIn("S2 28", result["successMessage"])
        self.assertIn("S3 27", result["successMessage"])
        self.assertEqual(result["afterRejected"], result["beforeRejected"])
        self.assertIn("S2", result["failureMessage"])
        self.assertEqual(list(result["twoSequenceMaps"]), ["2"])
        self.assertEqual(len(result["twoSequenceMaps"]["2"]), 1)

    def test_timeline_crosslink_visualization(self) -> None:
        source, parser = parse_page()

        self.assertIn("crosslink-timelines", parser.elements)
        self.assertIn("anchor-connectors", parser.elements)
        self.assertIn("anchor-marker", source)
        self.assertRegex(source, r"\.anchor-connectors\s*\{[^}]*pointer-events:\s*none")

    def test_trilinear_intensity_sampling(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const volume = {width: 2, height: 2, depth: 2, data: [0, 10, 20, 30, 40, 50, 60, 70]};
  return {
    center: C.sampleTrilinear(volume, 0.5, 0.5, 0.5),
    corner: C.sampleTrilinear(volume, 1, 1, 1),
    outsideX: C.sampleTrilinear(volume, -0.01, 0, 0),
    outsideZ: C.sampleTrilinear(volume, 0, 0, 2.01)
  };
})()
"""
        )

        self.assertEqual(result["center"], 35)
        self.assertEqual(result["corner"], 70)
        self.assertEqual(result["outsideX"], 0)
        self.assertEqual(result["outsideZ"], 0)

    def test_standard_orthogonal_reslices(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const data = [];
  for (let z = 0; z < 3; z += 1) {
    for (let y = 0; y < 3; y += 1) {
      for (let x = 0; x < 3; x += 1) data.push(x + 10 * y + 100 * z);
    }
  }
  const volume = {
    width: 3, height: 3, depth: 3, data,
    pixelSpacingX: 1, pixelSpacingY: 2, sliceSpacing: 4
  };
  const center = {x: 1, y: 1, z: 1};
  const red = buffer => Array.from(buffer).filter((_, index) => index % 4 === 0);
  const axPlane = C.makeOrthogonalPlane("AX", volume, center);
  const corPlane = C.makeOrthogonalPlane("COR", volume, center);
  const sagPlane = C.makeOrthogonalPlane("SAG", volume, center);
  return {
    ax: red(C.reslicePlane(volume, {...axPlane, mmPerPixelX: 1, mmPerPixelY: 2}, 3, 3)),
    cor: red(C.reslicePlane(volume, {...corPlane, mmPerPixelX: 1, mmPerPixelY: 4}, 3, 3)),
    sag: red(C.reslicePlane(volume, {...sagPlane, mmPerPixelX: 2, mmPerPixelY: 4}, 3, 3)),
    labels: {ax: axPlane.labels, cor: corPlane.labels, sag: sagPlane.labels}
  };
})()
"""
        )

        self.assertEqual(result["ax"], [100, 101, 102, 110, 111, 112, 120, 121, 122])
        self.assertEqual(result["cor"], [10, 11, 12, 110, 111, 112, 210, 211, 212])
        self.assertEqual(result["sag"], [1, 11, 21, 101, 111, 121, 201, 211, 221])
        self.assertEqual(result["labels"]["ax"], {"left": "R", "right": "L", "top": "A", "bottom": "P"})
        self.assertEqual(result["labels"]["cor"]["top"], "S")
        self.assertEqual(result["labels"]["sag"]["right"], "P")

    def test_arbitrary_oblique_reslice(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const volume = {pixelSpacingX: 1, pixelSpacingY: 1, sliceSpacing: 5};
  const center = {x: 12.5, y: 8.25, z: 4.5};
  const plane = C.makeObliquePlane(volume, center, {azimuth: 35, tilt: -22, roll: 17});
  const reset = C.makeObliquePlane(volume, center, {azimuth: 0, tilt: 0, roll: 0});
  const dot = (a, b) => a.x * b.x + a.y * b.y + a.z * b.z;
  const length = vector => Math.sqrt(dot(vector, vector));
  return {
    center: plane.center,
    lengths: [length(plane.u), length(plane.v), length(plane.normal)],
    dots: [dot(plane.u, plane.v), dot(plane.u, plane.normal), dot(plane.v, plane.normal)],
    reset: {center: reset.center, u: reset.u, v: reset.v, normal: reset.normal}
  };
})()
"""
        )

        self.assertEqual(result["center"], {"x": 12.5, "y": 8.25, "z": 4.5})
        for length in result["lengths"]:
            self.assertAlmostEqual(length, 1, places=10)
        for dot in result["dots"]:
            self.assertAlmostEqual(dot, 0, places=10)
        self.assertEqual(result["reset"]["center"], result["center"])
        self.assertEqual(result["reset"]["u"], {"x": 1, "y": 0, "z": 0})
        self.assertEqual(result["reset"]["v"], {"x": 0, "y": 1, "z": 0})
        self.assertEqual(result["reset"]["normal"], {"x": 0, "y": 0, "z": 1})

    def test_crosslinked_mpr_location(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  const volume = {pixelSpacingX: 1, pixelSpacingY: 1, sliceSpacing: 5};
  const plane = C.makeOrthogonalPlane("AX", volume, {x: 20, y: 30, z: 50.4});
  return {z: plane.center.z, axialFrame: Math.round(plane.center.z)};
})()
"""
        )

        self.assertEqual(result["z"], 50.4)
        self.assertEqual(result["axialFrame"], 50)

    def test_progressive_reslice_quality(self) -> None:
        result = run_core(
            r"""
(() => {
  const C = ImageStackMprCore;
  return {
    plan: C.progressiveRenderPlan(800, 600, 2, 5),
    current: C.isRenderGenerationCurrent(5, 5),
    stale: C.isRenderGenerationCurrent(4, 5),
    narrow: C.progressiveRenderPlan(100, 50, 1, 6)
  };
})()
"""
        )

        self.assertEqual(result["plan"]["preview"], {"width": 256, "height": 192})
        self.assertEqual(result["plan"]["full"], {"width": 1024, "height": 768})
        self.assertEqual(result["plan"]["delayMs"], 120)
        self.assertEqual(result["plan"]["generation"], 5)
        self.assertTrue(result["current"])
        self.assertFalse(result["stale"])
        self.assertEqual(result["narrow"]["preview"], {"width": 100, "height": 50})
        self.assertEqual(result["narrow"]["full"], {"width": 100, "height": 50})

    def test_basic_image_interaction_bindings(self) -> None:
        source, parser = parse_page()

        for element_id in (
            "sync-navigation",
            "sync-intensity",
            "fit-view",
            "reset-view",
            "invert-view",
            "oblique-azimuth",
            "oblique-tilt",
            "oblique-roll",
            "oblique-reset",
        ):
            self.assertIn(element_id, parser.elements)
        self.assertIn('addEventListener("wheel"', source)
        self.assertIn('addEventListener("pointerdown"', source)
        self.assertIn('addEventListener("pointermove"', source)
        self.assertIn('addEventListener("contextmenu"', source)
        self.assertIn("event.ctrlKey || event.metaKey", source)
        self.assertIn("event.button === 2", source)
        self.assertNotRegex(source, r"\bHU\b|Window Level|DICOM")

    def test_hover_keyboard_and_reversed_wheel_zoom(self) -> None:
        result = run_crosslink_interaction_probe()

        self.assertGreater(result["syncedPlus"]["2"], 1)
        self.assertEqual(
            result["syncedPlus"]["1"], result["syncedPlus"]["2"]
        )
        self.assertEqual(
            result["syncedPlus"]["3"], result["syncedPlus"]["2"]
        )
        self.assertEqual(result["unsyncedMinus"]["1"], 1)
        self.assertLess(result["unsyncedMinus"]["2"], 1)
        self.assertEqual(result["unsyncedMinus"]["3"], 1)
        self.assertEqual(result["noHover"], result["beforeNoHover"])
        self.assertGreater(result["wheelDown"], result["wheelStart"])
        self.assertLess(result["wheelUp"], result["wheelDown"])

    def test_responsive_comparison_workspace(self) -> None:
        source, parser = parse_page()

        self.assertIn("primary-mpr-grid", parser.elements)
        self.assertIn("secondary-mpr-regions", parser.elements)
        self.assertIn("@media (min-width: 1400px)", source)
        self.assertRegex(source, r"@media \(max-width: 900px\)[\s\S]*\.mpr-layout")
        self.assertIn("grid-template-columns: minmax(0, 2fr) minmax(320px, 1fr)", source)

    def test_portrait_crosslink_viewports_stack_vertically(self) -> None:
        result = measure_crosslink_orientation_layout()

        self.assertTrue(result["portraitMedia"])
        self.assertFalse(result["landscapeMedia"])
        self.assertEqual(result["portraitRows"], 3)
        self.assertTrue(all(result["portraitFullWidth"]))
        self.assertLess(result["landscapeRows"], 3)

    def test_unknown_geometry_warning_and_copy(self) -> None:
        source, parser = parse_page()

        self.assertIn("geometry-warning", parser.elements)
        self.assertIn("比例未知", source)
        self.assertIn("僅供定位", source)
        self.assertNotIn("可供量測", source)


if __name__ == "__main__":
    unittest.main()
