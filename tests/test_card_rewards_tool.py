from __future__ import annotations

import io
import base64
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import unittest
from collections.abc import Callable
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from html.parser import HTMLParser
from pathlib import Path
from contextlib import redirect_stderr
from unittest import mock

from scripts.build_card_rewards_tool import (
    DATA_END,
    DATA_START,
    BuildError,
    build_output,
    build_dataset,
    main,
    parse_document,
    read_embedded_dataset,
    replace_embedded_dataset,
    serialize_dataset,
)


ROOT = Path(__file__).parents[1]
UTF8_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


class ToolPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: dict[str, dict[str, str]] = {}
        self.external_assets: list[str] = []
        self.iframes: list[str] = []
        self.core_source = ""
        self.runtime_source = ""
        self._script_id: str | None = None
        self._script_parts: list[str] = []
        self._is_runtime_script = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {"tag": tag, **{name: value or "" for name, value in attrs}}
        if element_id := attributes.get("id"):
            self.elements[element_id] = attributes
        if tag == "iframe":
            self.iframes.append(attributes.get("src", ""))
        for name in ("src", "href"):
            value = attributes.get(name, "")
            is_external = value.startswith(("http://", "https://", "//"))
            if value and is_external and (name == "src" or tag == "link"):
                self.external_assets.append(value)
        if tag == "script":
            self._script_id = attributes.get("id")
            self._script_parts = []
            self._is_runtime_script = (
                self._script_id != "card-rewards-core"
                and attributes.get("type") != "application/json"
            )

    def handle_data(self, data: str) -> None:
        if self._script_id == "card-rewards-core" or self._is_runtime_script:
            self._script_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._script_id == "card-rewards-core":
            self.core_source = "".join(self._script_parts)
        if tag == "script" and self._is_runtime_script:
            self.runtime_source = "".join(self._script_parts)
        if tag == "script":
            self._script_id = None
            self._script_parts = []
            self._is_runtime_script = False


def parse_tool_page() -> ToolPageParser:
    parser = ToolPageParser()
    parser.feed((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"))
    return parser


def run_core(expression: str, filter_fixtures: dict[str, dict[str, object]] | None = None) -> object:
    parser = parse_tool_page()
    dataset = json.loads(read_embedded_dataset((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")))
    payload = json.dumps(
        {
            "core": parser.core_source,
            "cards": dataset["cards"],
            "expression": expression,
            "filterFixtures": filter_fixtures or {},
        },
        ensure_ascii=False,
    )
    runner = r'''
const fs = require("fs");
const vm = require("vm");
const payload = JSON.parse(fs.readFileSync(0, "utf8"));
if (!payload.core) throw new Error("missing card-rewards-core script");
const asFilterState = (filters) => ({
  ...filters,
  facets: new Set(filters.facets || []),
  coverage: new Set(filters.coverage || []),
  productTypes: new Set(filters.productTypes || [])
});
const filterFixtures = Object.fromEntries(
  Object.entries(payload.filterFixtures).map(([name, filters]) => [name, asFilterState(filters)])
);
const context = vm.createContext({ CARDS: payload.cards, FILTER_FIXTURES: filterFixtures, Set, String, Object, Array, JSON });
vm.runInContext(payload.core, context, { filename: "card-rewards-core.js" });
process.stdout.write(JSON.stringify(vm.runInContext(payload.expression, context, { filename: "card-rewards-expression.js" })));
'''
    result = subprocess.run(
        ["node", "-e", runner],
        input=payload,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=UTF8_ENV,
        check=False,
    )
    if result.returncode:
        raise AssertionError(result.stderr.strip())
    return json.loads(result.stdout)


def run_runtime(dataset: dict[str, object]) -> dict[str, object]:
    parser = parse_tool_page()
    payload = json.dumps(
        {"core": parser.core_source, "runtime": parser.runtime_source, "dataset": dataset},
        ensure_ascii=False,
    )
    runner = r'''
const fs = require("fs");
const vm = require("vm");
const payload = JSON.parse(fs.readFileSync(0, "utf8"));
class FakeElement {
  constructor(id) {
    this.id = id;
    this.children = [];
    this.textContent = "";
    this.hidden = false;
    this.value = "";
    this.disabled = false;
    this.mutations = 0;
    this.classList = { values: new Set(), add: value => this.classList.values.add(value), contains: value => this.classList.values.has(value) };
  }
  append(...children) { this.children.push(...children); this.mutations += 1; }
  replaceChildren(...children) { this.children = children; this.mutations += 1; }
  setAttribute() {}
  addEventListener() {}
  focus() {}
}
const ids = ["app", "fatal-error", "search", "result-count", "clear-filters", "facet-controls", "coverage-controls", "type-controls", "card-grid", "empty-state", "empty-clear", "compare-tray", "compare-count", "compare-selected", "compare-limit", "compare-open", "compare-dialog", "compare-close", "comparison-content", "detail-dialog", "detail-title", "detail-content", "detail-close", "card-rewards-data"];
const elements = Object.fromEntries(ids.map(id => [id, new FakeElement(id)]));
elements["fatal-error"].hidden = true;
elements["card-rewards-data"].textContent = JSON.stringify(payload.dataset);
const document = {
  getElementById: id => elements[id] || null,
  createElement: tag => new FakeElement(tag)
};
const context = vm.createContext({ document, Set, String, Object, Array, JSON });
vm.runInContext(payload.core, context, { filename: "card-rewards-core.js" });
vm.runInContext(payload.runtime, context, { filename: "card-rewards-runtime.js" });
const fatalText = elements["fatal-error"].children.map(child => child.textContent).join(" ");
process.stdout.write(JSON.stringify({
  fatalText,
  fatalHidden: elements["fatal-error"].hidden,
  controlsHidden: elements.app.classList.contains("is-fatal"),
  facetControlMutations: elements["facet-controls"].mutations
}));
'''
    result = subprocess.run(
        ["node", "-e", runner],
        input=payload,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=UTF8_ENV,
        check=False,
    )
    if result.returncode:
        raise AssertionError(result.stderr.strip())
    return json.loads(result.stdout)


def find_headless_browser() -> str:
    candidates = (
        Path(os.environ.get("PROGRAMFILES", r"C:\\Program Files")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", r"C:\\Program Files (x86)")) / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("PROGRAMFILES", r"C:\\Program Files")) / "Microsoft/Edge/Application/msedge.exe",
    )
    browser = next((candidate for candidate in candidates if candidate.is_file()), None)
    if browser is None:
        raise unittest.SkipTest("Chrome 或 Edge 不可用，無法執行 headless interaction probe")
    return str(browser)


class DevToolsWebSocket:
    def __init__(self, websocket_url: str) -> None:
        parsed = urlparse(websocket_url)
        self.socket = socket.create_connection((parsed.hostname, parsed.port), timeout=10)
        self.socket.settimeout(10)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        target_path = parsed.path if not parsed.query else f"{parsed.path}?{parsed.query}"
        request = (
            f"GET {target_path} HTTP/1.1\r\n"
            f"Host: {parsed.netloc}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\nOrigin: http://localhost\r\n\r\n"
        )
        self.socket.sendall(request.encode("ascii"))
        response = b""
        while b"\r\n\r\n" not in response:
            response += self.socket.recv(4096)
        if not response.startswith(b"HTTP/1.1 101"):
            self.socket.close()
            raise AssertionError(f"DevTools WebSocket upgrade failed: {response.decode('utf-8', errors='replace')}")
        self.next_id = 1
        self.events: list[dict[str, object]] = []

    def close(self) -> None:
        self.socket.close()

    def _send_frame(self, opcode: int, payload: bytes) -> None:
        mask = os.urandom(4)
        length = len(payload)
        header = bytes([0x80 | opcode])
        if length < 126:
            header += bytes([0x80 | length])
        elif length < 65536:
            header += bytes([0x80 | 126]) + struct.pack("!H", length)
        else:
            header += bytes([0x80 | 127]) + struct.pack("!Q", length)
        masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        self.socket.sendall(header + mask + masked)

    def _receive_exactly(self, size: int) -> bytes:
        payload = b""
        while len(payload) < size:
            chunk = self.socket.recv(size - len(payload))
            if not chunk:
                raise AssertionError("DevTools WebSocket closed unexpectedly")
            payload += chunk
        return payload

    def _receive_message(self) -> dict[str, object]:
        first, second = self._receive_exactly(2)
        opcode = first & 0x0F
        masked = bool(second & 0x80)
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", self._receive_exactly(2))[0]
        elif length == 127:
            length = struct.unpack("!Q", self._receive_exactly(8))[0]
        mask = self._receive_exactly(4) if masked else b""
        payload = self._receive_exactly(length)
        if masked:
            payload = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        if opcode == 0x9:
            self._send_frame(0xA, payload)
            return self._receive_message()
        if opcode == 0x8:
            raise AssertionError("DevTools WebSocket closed unexpectedly")
        if opcode != 0x1:
            return self._receive_message()
        return json.loads(payload.decode("utf-8"))

    def command(self, method: str, params: dict[str, object] | None = None) -> dict[str, object]:
        message_id = self.next_id
        self.next_id += 1
        self._send_frame(0x1, json.dumps({"id": message_id, "method": method, "params": params or {}}).encode("utf-8"))
        while True:
            message = self._receive_message()
            if message.get("id") == message_id:
                if "error" in message:
                    raise AssertionError(f"DevTools {method} failed: {message['error']}")
                return message["result"]
            self.events.append(message)

    def wait_for_event(self, method: str) -> dict[str, object]:
        for index, event in enumerate(self.events):
            if event.get("method") == method:
                return self.events.pop(index)
        while True:
            event = self._receive_message()
            if event.get("method") == method:
                return event
            self.events.append(event)


def wait_for_devtools_port(profile: Path, browser: subprocess.Popen[str]) -> int:
    port_file = profile / "DevToolsActivePort"
    deadline = time.monotonic() + 10
    while not port_file.is_file():
        if browser.poll() is not None:
            raise AssertionError("Chrome exited before publishing the DevTools port")
        if time.monotonic() >= deadline:
            raise AssertionError("Chrome did not publish the DevTools port")
        time.sleep(0.01)
    return int(port_file.read_text(encoding="utf-8").splitlines()[0])


def devtools_json(url: str, *, method: str = "GET") -> dict[str, object]:
    with urlopen(Request(url, method=method), timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def evaluate(connection: DevToolsWebSocket, expression: str) -> object:
    result = connection.command("Runtime.evaluate", {"expression": expression, "returnByValue": True})
    if "exceptionDetails" in result:
        raise AssertionError(f"DevTools evaluation failed: {result['exceptionDetails']}")
    return result["result"].get("value")


def run_headless_interaction_probe() -> dict[str, object]:
    setup_expression = r'''
(() => {
  const result = { ok: false, errors: [] };
  const check = (condition, message) => { if (!condition) result.errors.push(message); };
  try {
    const search = document.getElementById("search");
    search.value = "路易莎";
    search.dispatchEvent(new Event("input", { bubbles: true }));
    const louisaCards = [...document.querySelectorAll("#card-grid .card")];
    check(louisaCards.length === 1 && louisaCards[0].textContent.includes("DAWAY"), "路易莎搜尋結果不正確");
    document.getElementById("clear-filters").click();
    const addNext = () => [...document.querySelectorAll("#card-grid .secondary-button")].find(button => button.textContent === "加入比較");
    for (let index = 0; index < 3; index += 1) {
      const button = addNext();
      check(Boolean(button), `第 ${index + 1} 張加入比較按鈕不存在`);
      if (!button) continue;
      const product = button.closest(".card").querySelector("h2").textContent;
      button.focus();
      check(document.activeElement === button, `第 ${index + 1} 張加入比較按鈕無法取得焦點`);
      button.click();
      const rebuiltCard = [...document.querySelectorAll("#card-grid .card")].find(card => card.querySelector("h2").textContent === product);
      const removeButton = rebuiltCard && [...rebuiltCard.querySelectorAll("button")].find(control => control.textContent === "移出比較");
      check(document.activeElement === removeButton, `${product} 加入比較後未回到重建的移出比較按鈕`);
    }
    const fourth = addNext();
    check(document.getElementById("compare-count").textContent.includes("3"), "比較數量未維持 3");
    check(document.getElementById("compare-count").textContent.includes("最多比較 3 項產品"), "三項比較時缺少 live 最大數量公告");
    check(Boolean(fourth) && fourth.disabled, "第四張加入比較按鈕未停用");
    check(Boolean(fourth) && fourth.getAttribute("aria-describedby") === "compare-limit", "第四張加入比較按鈕缺少可存取說明");
    check(!document.getElementById("compare-limit").hidden && document.getElementById("compare-limit").textContent.includes("最多比較 3 項產品"), "第四張加入比較按鈕的可見說明缺少最大數量文字");
    if (fourth) fourth.click();
    check(document.getElementById("compare-count").textContent.includes("3"), "第四張卡改變了比較數量");
    document.getElementById("compare-open").click();
    const comparison = document.getElementById("comparison-content").textContent;
    check(comparison.includes("國內一般消費") && comparison.includes("海外消費"), "比較表缺少國內或海外列");
    document.getElementById("compare-close").click();
    const cubeCard = [...document.querySelectorAll("#card-grid .card")].find(card => card.textContent.includes("CUBE"));
    const detailButton = cubeCard && [...cubeCard.querySelectorAll("button")].find(button => button.textContent === "查看詳情");
    check(Boolean(detailButton), "CUBE 詳情按鈕不存在");
    if (detailButton) { detailButton.focus(); detailButton.click(); }
    const detail = document.getElementById("detail-content");
    check(detail.textContent.includes("部分期間") && detail.textContent.includes("不確定事項"), "CUBE 詳情缺少部分期間或不確定事項");
    check(Boolean(detail.querySelector('a[href^="https://"]')), "CUBE 詳情缺少 HTTPS 官方來源");
    document.getElementById("detail-close").click();
    check(document.activeElement === detailButton, "詳情明確關閉後未回到原始開啟按鈕");
    if (detailButton) { detailButton.focus(); detailButton.click(); }
    const detailDialog = document.getElementById("detail-dialog");
    result.escapeDialogWasOpen = Boolean(detailDialog.open && detailDialog.matches(":modal"));
    check(result.escapeDialogWasOpen, "DevTools Escape 前詳情 dialog 未以原生 modal 開啟");
    window.__cardRewardsEscapeProbe = { result, detailButton, detailDialog };
  } catch (error) {
    result.errors.push(String(error));
  }
  return result;
})()
'''
    finish_expression = r'''
(() => {
  const probe = window.__cardRewardsEscapeProbe;
  const { result, detailButton, detailDialog } = probe;
  const nativeEscape = !detailDialog.open && document.activeElement === detailButton;
  if (!nativeEscape) result.errors.push("原生 Escape 關閉後未回到原始開啟按鈕");
  result.nativeEscape = nativeEscape;
  result.ok = result.errors.length === 0;
  return result;
})()
'''
    with tempfile.TemporaryDirectory() as temp:
        temporary_root = Path(temp)
        page = temporary_root / "card-rewards.html"
        page.write_text((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"), encoding="utf-8")
        profile = temporary_root / "browser-profile"
        browser = subprocess.Popen(
            [
                find_headless_browser(), "--headless=new", "--disable-gpu", "--disable-extensions", "--no-first-run",
                "--remote-debugging-port=0", "--remote-allow-origins=*", "--window-size=1200,900", f"--user-data-dir={profile}", "about:blank",
            ],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=UTF8_ENV,
        )
        connection: DevToolsWebSocket | None = None
        try:
            port = wait_for_devtools_port(profile, browser)
            targets = devtools_json(f"http://127.0.0.1:{port}/json/list")
            target = next((item for item in targets if item.get("type") == "page"), None)
            if target is None:
                raise AssertionError("Chrome did not expose a page target for the headless probe")
            connection = DevToolsWebSocket(str(target["webSocketDebuggerUrl"]))
            connection.command("Page.enable")
            connection.command("Page.navigate", {"url": page.as_uri()})
            connection.wait_for_event("Page.loadEventFired")
            evaluate(connection, setup_expression)
            connection.command("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Escape", "code": "Escape", "windowsVirtualKeyCode": 27, "nativeVirtualKeyCode": 27})
            connection.command("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Escape", "code": "Escape", "windowsVirtualKeyCode": 27, "nativeVirtualKeyCode": 27})
            result = evaluate(connection, finish_expression)
        finally:
            if connection is not None:
                connection.close()
            browser.terminate()
            browser.wait(timeout=10)
    if not isinstance(result, dict):
        raise AssertionError("headless probe did not return an object")
    return result


def run_browser_probe(
    probe: str,
    *,
    width: int,
    height: int,
    source_transform: Callable[[str], str] | None = None,
) -> dict[str, object]:
    expressions = {
        "source-links": r'''
(() => {
  const detailButton = document.querySelector("[data-action='detail']");
  if (!detailButton) throw new Error("detail button missing");
  detailButton.click();
  const links = [...document.querySelectorAll(".evidence-sources a[href]")];
  return {
    sourceCount: links.length,
    allHttps: links.every(link => link.href.startsWith("https://")),
    allNoopenerNoreferrer: links.every(link => {
      const tokens = new Set(link.rel.split(/\s+/).filter(Boolean));
      return tokens.has("noopener") && tokens.has("noreferrer");
    })
  };
})()
''',
        "invalid-schema": r'''
(() => {
  const fatal = document.getElementById("fatal-error");
  return {
    fatalVisible: !fatal.hidden && getComputedStyle(fatal).display !== "none",
    fatalText: fatal.textContent,
    controlsHidden: document.getElementById("app").classList.contains("is-fatal")
  };
})()
''',
        "mobile": r'''
(() => {
  const detailButton = document.querySelector("[data-action='detail']");
  if (!detailButton) throw new Error("detail button missing");
  detailButton.click();
  const dialog = document.getElementById("detail-dialog");
  const close = document.getElementById("detail-close").getBoundingClientRect();
  return {
    viewportWidth: document.documentElement.clientWidth,
    cardColumns: getComputedStyle(document.getElementById("card-grid")).gridTemplateColumns,
    bodyOverflow: document.documentElement.scrollWidth <= document.documentElement.clientWidth,
    touchTargetHeight: detailButton.getBoundingClientRect().height,
    detailOpen: dialog.open,
    detailMode: getComputedStyle(dialog).getPropertyValue("--detail-mode").trim(),
    closeVisible: close.top >= 0 && close.bottom <= window.innerHeight
  };
})()
''',
    }
    if probe not in expressions:
        raise ValueError(f"unknown browser probe: {probe}")
    source = (ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")
    if source_transform is not None:
        source = source_transform(source)
    with tempfile.TemporaryDirectory() as temp:
        temporary_root = Path(temp)
        page = temporary_root / "card-rewards.html"
        page.write_text(source, encoding="utf-8")
        profile = temporary_root / "browser-profile"
        browser = subprocess.Popen(
            [
                find_headless_browser(), "--headless=new", "--disable-gpu", "--disable-extensions", "--no-first-run",
                "--remote-debugging-port=0", "--remote-allow-origins=*", f"--window-size={width},{height}", f"--user-data-dir={profile}", "about:blank",
            ],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=UTF8_ENV,
        )
        connection: DevToolsWebSocket | None = None
        try:
            port = wait_for_devtools_port(profile, browser)
            targets = devtools_json(f"http://127.0.0.1:{port}/json/list")
            target = next((item for item in targets if item.get("type") == "page"), None)
            if target is None:
                raise AssertionError("Chrome did not expose a page target for the browser probe")
            connection = DevToolsWebSocket(str(target["webSocketDebuggerUrl"]))
            connection.command("Page.enable")
            connection.command(
                "Emulation.setDeviceMetricsOverride",
                {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": width <= 720},
            )
            connection.command("Page.navigate", {"url": page.as_uri()})
            connection.wait_for_event("Page.loadEventFired")
            result = evaluate(connection, expressions[probe])
        finally:
            if connection is not None:
                connection.close()
            browser.terminate()
            browser.wait(timeout=10)
    if not isinstance(result, dict):
        raise AssertionError("browser probe did not return an object")
    return result


class CardRewardsAcceptanceTests(unittest.TestCase):
    def test_offline_page_has_no_automatic_network_surface(self) -> None:
        parser = parse_tool_page()

        self.assertEqual([], parser.external_assets)
        self.assertEqual([], parser.iframes)
        source = (ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")
        for forbidden in ("fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "localStorage"):
            self.assertNotIn(forbidden, source)

    def test_all_generated_official_links_are_https_and_safe(self) -> None:
        result = run_browser_probe("source-links", width=1200, height=900)

        self.assertGreater(result["sourceCount"], 0)
        self.assertTrue(result["allHttps"])
        self.assertTrue(result["allNoopenerNoreferrer"])

    def test_corpus_text_is_not_executed_as_html(self) -> None:
        source = (ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")

        self.assertNotRegex(source, r"\.innerHTML\s*=.*(?:card|section|source|dataset)")

    def test_invalid_schema_shows_visible_failure_without_network_fallback(self) -> None:
        result = run_browser_probe(
            "invalid-schema",
            width=1200,
            height=900,
            source_transform=lambda source: source.replace(
                '"schemaVersion": "1"', '"schemaVersion": "unsupported"', 1
            ),
        )

        self.assertTrue(result["fatalVisible"])
        self.assertIn("資料無法載入", result["fatalText"])
        self.assertTrue(result["controlsHidden"])

    def test_mobile_layout_uses_a_bottom_sheet_with_accessible_controls(self) -> None:
        result = run_browser_probe("mobile", width=390, height=844)

        self.assertEqual(390, result["viewportWidth"])
        self.assertEqual(1, len(result["cardColumns"].split()))
        self.assertTrue(result["bodyOverflow"])
        self.assertGreaterEqual(result["touchTargetHeight"], 44)
        self.assertTrue(result["detailOpen"])
        self.assertEqual("bottom-sheet", result["detailMode"])
        self.assertTrue(result["closeVisible"])


class CardRewardsInterfaceTests(unittest.TestCase):
    def test_page_has_required_discovery_controls(self) -> None:
        parser = parse_tool_page()
        for element_id in (
            "app", "fatal-error", "search", "result-count", "clear-filters", "facet-controls",
            "coverage-controls", "type-controls", "card-grid", "empty-state", "compare-tray",
        ):
            self.assertIn(element_id, parser.elements)
        self.assertEqual("search", parser.elements["search"]["type"])

    def test_page_has_no_runtime_asset_or_network_dependency(self) -> None:
        parser = parse_tool_page()
        self.assertEqual([], parser.external_assets)
        source = (ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")
        self.assertNotRegex(source, r"\bfetch\s*\(")
        self.assertNotIn("XMLHttpRequest", source)

    def test_selection_stops_at_three_without_mutating_input(self) -> None:
        expression = """
        (() => {
          const original = ['first-ileo', 'first-green', 'sinopac-dawho'];
          const result = toggleSelection(original, 'sinopac-daway');
          return { original, result };
        })()
        """
        value = run_core(expression)
        self.assertEqual(["first-ileo", "first-green", "sinopac-dawho"], value["original"])
        self.assertEqual(value["original"], value["result"]["ids"])
        self.assertTrue(value["result"]["limitReached"])

    def test_selection_can_remove_and_readd_a_product(self) -> None:
        value = run_core("toggleSelection(['first-ileo', 'first-green'], 'first-ileo')")
        self.assertEqual(["first-green"], value["ids"])
        self.assertFalse(value["limitReached"])

    def test_compare_and_detail_use_native_dialogs_with_labels(self) -> None:
        parser = parse_tool_page()
        self.assertEqual("dialog", parser.elements["compare-dialog"]["tag"])
        self.assertEqual("dialog", parser.elements["detail-dialog"]["tag"])
        self.assertEqual("detail-title", parser.elements["detail-dialog"]["aria-labelledby"])
        self.assertIn("aria-live", parser.elements["compare-count"])

    def test_headless_interaction_probe(self) -> None:
        result = run_headless_interaction_probe()
        self.assertTrue(result["ok"], result["errors"])
        self.assertTrue(result.get("escapeDialogWasOpen"), "probe did not prove the detail dialog was open before Escape")
        self.assertTrue(result.get("nativeEscape"), "probe did not prove native Escape dialog closure")

    def test_core_search_matches_bank_alias_merchant_and_payment(self) -> None:
        self.assertTrue(run_core("cardMatchesQuery(CARDS.find(c => c.id === 'taishin-richart-gogo'), '@gogo')"))
        self.assertTrue(run_core("cardMatchesQuery(CARDS.find(c => c.id === 'sinopac-daway'), '路易莎')"))
        self.assertTrue(run_core("cardMatchesQuery(CARDS.find(c => c.id === 'esun-unicard'), '全支付')"))
        self.assertFalse(run_core("cardMatchesQuery(CARDS.find(c => c.id === 'esun-pi'), 'Costco')"))

    def test_filter_groups_are_or_within_group_and_and_across_groups(self) -> None:
        expression = """
        filterCards(CARDS, {
          query: '',
          facets: new Set(['line-pay', 'ipass-money']),
          coverage: new Set(['complete']),
          productTypes: new Set()
        }).map(card => card.id)
        """
        result = run_core(expression)
        self.assertIn("esun-unicard", result)
        self.assertNotIn("esun-pi", result)

    def test_malformed_card_shape_shows_fatal_before_filter_controls_render(self) -> None:
        dataset = json.loads(read_embedded_dataset((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")))
        dataset["cards"][0].pop("facetIds")

        result = run_runtime(dataset)

        self.assertFalse(result["fatalHidden"])
        self.assertTrue(result["controlsHidden"])
        self.assertIn("資料無法載入", result["fatalText"])
        self.assertEqual(0, result["facetControlMutations"])

    def test_malformed_comparison_render_field_shows_fatal_before_render(self) -> None:
        dataset = json.loads(read_embedded_dataset((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")))
        dataset["cards"][0]["comparison"]["domestic"] = {"not": "renderable text"}

        result = run_runtime(dataset)

        self.assertFalse(result["fatalHidden"])
        self.assertTrue(result["controlsHidden"])
        self.assertIn("資料無法載入", result["fatalText"])
        self.assertEqual(0, result["facetControlMutations"])

    def test_non_string_badge_shows_fatal_before_render(self) -> None:
        dataset = json.loads(read_embedded_dataset((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8")))
        dataset["cards"][0]["badges"][0] = {"not": "a badge label"}

        result = run_runtime(dataset)

        self.assertFalse(result["fatalHidden"])
        self.assertTrue(result["controlsHidden"])
        self.assertIn("資料無法載入", result["fatalText"])
        self.assertEqual(0, result["facetControlMutations"])


class CardRewardsDatasetTests(unittest.TestCase):
    def test_dataset_card_product_types_match_phase_one_frontmatter(self) -> None:
        cards = build_dataset(ROOT)["cards"]
        corpus_root = ROOT / "docs/card-rewards/2026-h2"
        expected = [
            parse_document(corpus_root / "cards" / f"{card['id']}.md", corpus_root=corpus_root)["metadata"]["product_type"]
            for card in cards
        ]

        self.assertEqual(expected, [card.get("productType") for card in cards])

    def test_dataset_contains_exact_approved_products_and_payments(self) -> None:
        dataset = build_dataset(ROOT)
        cards = dataset["cards"]
        payments = dataset["payments"]

        self.assertEqual("1", dataset["schemaVersion"])
        self.assertEqual("2026-08-18", dataset["auditDate"])
        self.assertEqual("2026-08-01", dataset["targetFrom"])
        self.assertEqual("2026-12-31", dataset["targetTo"])
        self.assertEqual({"complete": 9, "partial": 9, "unavailable": 0}, dataset["coverageCounts"])
        self.assertEqual(15, len(cards))
        self.assertEqual(15, len({card["id"] for card in cards}))
        self.assertEqual(["line-pay", "ipass-money", "px-pay"], [item["id"] for item in payments])
        self.assertTrue(all(len(item["rows"]) == 15 for item in payments))

    def test_card_record_preserves_comparison_sections_sources_and_badges(self) -> None:
        dataset = build_dataset(ROOT)
        cards = {card["id"]: card for card in dataset["cards"]}
        cube = cards["cathay-cube"]

        self.assertEqual("國泰世華 CUBE 卡", cube["product"])
        self.assertEqual("partial", cube["coverageStatus"])
        self.assertIn("8/3", cube["comparison"]["domestic"])
        self.assertIn("2.5%", cube["comparison"]["overseas"])
        self.assertIn("partial", cube["badges"])
        self.assertIn("overseas", cube["facetIds"])
        self.assertIn("CUBE", cube["searchAliases"])
        self.assertTrue(cube["sections"]["uncertainties"]["blocks"])
        self.assertTrue(all(source["url"].startswith("https://") for source in cube["sources"]))

    def test_payment_names_map_back_to_stable_product_ids(self) -> None:
        dataset = build_dataset(ROOT)
        line_pay = next(item for item in dataset["payments"] if item["id"] == "line-pay")
        rows = {row["productId"]: row for row in line_pay["rows"]}

        self.assertEqual("supported", rows["sinopac-daway"]["supported"])
        self.assertIn("26.5%", rows["sinopac-daway"]["stacking"])
        self.assertEqual("not officially confirmed", rows["esun-pi"]["supported"])

    def test_serialized_dataset_is_deterministic_and_utf8_readable(self) -> None:
        first = serialize_dataset(build_dataset(ROOT))
        second = serialize_dataset(build_dataset(ROOT))

        self.assertEqual(first, second)
        self.assertIn("國泰世華 CUBE 卡", first)
        self.assertNotIn(str(ROOT), first)
        self.assertNotIn("generatedAt", first)
        self.assertEqual(json.loads(first), json.loads(second))

    def test_malformed_card_section_table_preserves_short_row_as_fallback(self) -> None:
        dataset = build_dataset(ROOT)
        cards = {card["id"]: card for card in dataset["cards"]}
        blocks = cards["ctbc-line-pay"]["sections"]["specialRewards"]["blocks"]
        fallback = next(block for block in blocks if block["type"] == "table-fallback")
        short_row = next(row for row in fallback["rows"] if len(row["cells"]) == 6)

        self.assertTrue(fallback["sourceRowWidthMismatch"])
        self.assertEqual(
            [
                "有效期間",
                "場景／通路",
                "總回饋",
                "組成",
                "舊戶條件",
                "回饋上限／推導可刷額",
                "登錄／名額",
            ],
            fallback["headers"],
        )
        self.assertEqual(
            [
                "2026-01-01 至 2026-12-31",
                "Hotels.com 臺灣網站指定「LINE Pay卡」網頁，代碼 `CTBCLP16`",
                "16% LINE POINTS",
                "已含一般 1%；不與 Hotels.com Rewards™ 併用 [來源 6]",
                "線上以 LINE Pay 卡付款、新臺幣，1-28 晚；2026 年預訂、2027-06-30 前完成入住，僅線上付款飯店，Pay at hotel 不適用；每筆 1,800 點 [來源 6]",
                "詳細頁稱每月首 450 次預訂；但官方總表稱每月 400 組，兩頁衝突，不選一方為完整名額 [來源 3][來源 6]",
            ],
            short_row["cells"],
        )

    def test_non_ctbc_section_row_width_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "repo"
            shutil.copytree(ROOT / "docs", fixture / "docs")
            card = fixture / "docs/card-rewards/2026-h2/cards/first-ileo.md"
            lines = card.read_text(encoding="utf-8").splitlines()
            start = lines.index("## 特殊回饋")
            end = lines.index("## 行動支付相容性")
            data_rows_started = False
            for index in range(start + 1, end):
                cells = lines[index].strip()[1:-1].split("|") if lines[index].strip().startswith("|") else []
                if cells and all(cell.strip(" -:") == "" for cell in cells):
                    data_rows_started = True
                    continue
                if data_rows_started and len(cells) == 8:
                    lines[index] = "|" + "|".join(cells[:-1]) + "|"
                    break
            else:
                self.fail("fixture did not contain a special-reward data row")
            card.write_text("\n".join(lines) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(BuildError, "cards/first-ileo.md: .*fixed row width"):
                build_dataset(fixture)

    def test_unknown_payment_product_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "repo"
            shutil.copytree(ROOT / "docs", fixture / "docs")
            payment = fixture / "docs/card-rewards/2026-h2/payments/line-pay.md"
            text = payment.read_text(encoding="utf-8").replace(
                "| 第一銀行 iLEO 卡 |", "| 不存在的產品 |", 1
            )
            payment.write_text(text, encoding="utf-8")

            with self.assertRaisesRegex(BuildError, "payment product.*不存在的產品"):
                build_dataset(fixture)

    def test_missing_required_card_section_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "repo"
            shutil.copytree(ROOT / "docs", fixture / "docs")
            card = fixture / "docs/card-rewards/2026-h2/cards/first-ileo.md"
            text = card.read_text(encoding="utf-8").replace("## 排除交易", "## 其他事項", 1)
            card.write_text(text, encoding="utf-8")

            with self.assertRaisesRegex(BuildError, "排除交易"):
                build_dataset(fixture)


class CardRewardsBuildTests(unittest.TestCase):
    def test_replace_embedded_dataset_changes_only_marked_block(self) -> None:
        source = f"before\n{DATA_START}\nold\n{DATA_END}\nafter\n"
        updated = replace_embedded_dataset(source, '{"schemaVersion": "1"}\n')

        self.assertTrue(updated.startswith(f"before\n{DATA_START}\n"))
        self.assertTrue(updated.endswith(f"{DATA_END}\nafter\n"))
        self.assertEqual(serialize_dataset({"schemaVersion": "1"}), read_embedded_dataset(updated))

    def test_replace_rejects_missing_or_duplicate_markers(self) -> None:
        with self.assertRaisesRegex(BuildError, "exactly one data marker pair"):
            replace_embedded_dataset("<html></html>", "{}\n")
        duplicate = f"{DATA_START}x{DATA_END}{DATA_START}y{DATA_END}"
        with self.assertRaisesRegex(BuildError, "exactly one data marker pair"):
            replace_embedded_dataset(duplicate, "{}\n")

    def test_read_rejects_duplicate_data_scripts(self) -> None:
        source = (
            f"{DATA_START}\n"
            '<script id="card-rewards-data" type="application/json">\n{}\n</script>\n'
            '<script id="card-rewards-data" type="application/json">\n{}\n</script>\n'
            f"{DATA_END}"
        )

        with self.assertRaisesRegex(BuildError, "exactly one card-rewards-data JSON script"):
            read_embedded_dataset(source)

    def test_read_rejects_raw_script_closer_or_invalid_json_payload(self) -> None:
        raw_closer = (
            f"{DATA_START}\n"
            '<script id="card-rewards-data" type="application/json">\n'
            '{"value": "</script>"}\n</script>\n'
            f"{DATA_END}"
        )
        invalid_json = (
            f"{DATA_START}\n"
            '<script id="card-rewards-data" type="application/json">\nnot JSON\n</script>\n'
            f"{DATA_END}"
        )

        with self.assertRaisesRegex(BuildError, "raw closing script token"):
            read_embedded_dataset(raw_closer)
        with self.assertRaisesRegex(BuildError, "valid JSON"):
            read_embedded_dataset(invalid_json)

    def test_read_allows_json_with_a_non_closing_script_token(self) -> None:
        source = (
            f"{DATA_START}\n"
            '<script id="card-rewards-data" type="application/json">\n'
            '{"value": "<script>"}\n</script>\n'
            f"{DATA_END}"
        )

        self.assertEqual(serialize_dataset({"value": "<script>"}), read_embedded_dataset(source))

    def test_checked_in_html_matches_generated_dataset(self) -> None:
        expected = serialize_dataset(build_dataset(ROOT))
        actual = read_embedded_dataset((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"))
        self.assertEqual(expected, actual)

    def test_cli_check_detects_one_byte_of_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "card-rewards.html"
            output.write_text((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"), encoding="utf-8")
            output.write_text(output.read_text(encoding="utf-8").replace('"schemaVersion": "1"', '"schemaVersion": "9"', 1), encoding="utf-8")
            before_check = output.read_bytes()
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_card_rewards_tool.py"), "--check", "--output", str(output)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=UTF8_ENV,
                check=False,
            )
            after_check = output.read_bytes()

        self.assertEqual(1, result.returncode)
        self.assertIn("embedded dataset drift", result.stderr)
        self.assertEqual(before_check, after_check)

    def test_build_then_check_canonicalizes_script_safe_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "repo"
            shutil.copytree(ROOT / "docs", fixture / "docs")
            card = fixture / "docs/card-rewards/2026-h2/cards/first-ileo.md"
            card.write_text(
                card.read_text(encoding="utf-8").replace(
                    "## 不確定事項", "## 不確定事項\n\n</script>", 1
                ),
                encoding="utf-8",
            )
            output = Path(tmp) / "card-rewards.html"
            output.write_text((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"), encoding="utf-8")

            self.assertIn("</script>", serialize_dataset(build_dataset(fixture)))
            self.assertTrue(build_output(fixture, output, check=False))
            self.assertIn(r"<\/script>", output.read_text(encoding="utf-8"))
            self.assertTrue(build_output(fixture, output, check=True))

    def test_build_then_check_escapes_mixed_case_closing_script_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "repo"
            shutil.copytree(ROOT / "docs", fixture / "docs")
            card = fixture / "docs/card-rewards/2026-h2/cards/first-ileo.md"
            card.write_text(
                card.read_text(encoding="utf-8").replace(
                    "## 不確定事項", "## 不確定事項\n\n</ScRiPt>", 1
                ),
                encoding="utf-8",
            )
            output = Path(tmp) / "card-rewards.html"
            output.write_text((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"), encoding="utf-8")

            self.assertIn("</ScRiPt>", serialize_dataset(build_dataset(fixture)))
            self.assertTrue(build_output(fixture, output, check=False))
            embedded = output.read_text(encoding="utf-8")
            self.assertNotIn("</ScRiPt>", embedded)
            self.assertIn(r"<\/ScRiPt>", embedded)
            self.assertTrue(build_output(fixture, output, check=True))

    def test_build_output_wraps_replace_errors_as_build_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "card-rewards.html"
            output.write_text((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"), encoding="utf-8")

            with mock.patch.object(Path, "replace", side_effect=OSError("replace blocked")):
                with self.assertRaisesRegex(BuildError, "cannot write HTML output"):
                    build_output(ROOT, output, check=False)

            self.assertEqual([], list(Path(tmp).glob("*.tmp")))

    def test_main_reports_temporary_cleanup_errors_as_build_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "card-rewards.html"
            output.write_text((ROOT / "tool/card-rewards.html").read_text(encoding="utf-8"), encoding="utf-8")
            stderr = io.StringIO()

            with (
                mock.patch.object(Path, "exists", return_value=True),
                mock.patch.object(Path, "unlink", side_effect=OSError("cleanup blocked")),
                redirect_stderr(stderr),
            ):
                self.assertEqual(1, main(["--output", str(output)]))

        self.assertIn("card rewards build: cannot clean temporary HTML output", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())
