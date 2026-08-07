from __future__ import annotations

import json
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path


HTML_PATH = Path(__file__).parents[1] / "tool" / "us-probe-ct-plane.html"


class ProbePageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.elements: dict[str, dict[str, str | None]] = {}
        self.interaction_script: list[str] = []
        self._in_interaction_script = False

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            self.elements[element_id] = attributes
        if tag == "script" and element_id == "interaction-logic":
            self._in_interaction_script = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_interaction_script:
            self._in_interaction_script = False

    def handle_data(self, data: str) -> None:
        if self._in_interaction_script:
            self.interaction_script.append(data)


def parse_page() -> ProbePageParser:
    parser = ProbePageParser()
    parser.feed(HTML_PATH.read_text(encoding="utf-8"))
    return parser


class ProbeInteractionTests(unittest.TestCase):
    def test_rotation_slider_uses_signed_clinical_angle_range(self) -> None:
        rotation = parse_page().elements["rot"]

        self.assertEqual(rotation["min"], "-180")
        self.assertEqual(rotation["max"], "180")

    def test_pointer_drag_uses_reduced_orbit_sensitivity(self) -> None:
        source = "".join(parse_page().interaction_script)
        result = run_interaction_logic(
            source,
            "orbitAfterPointerDrag(1, 2, 100, -50)",
        )

        self.assertAlmostEqual(result["theta"], 0.6)
        self.assertAlmostEqual(result["phi"], 2.2)

    def test_dicom_wheel_direction_is_reversed(self) -> None:
        source = "".join(parse_page().interaction_script)

        self.assertEqual(run_interaction_logic(source, "dicomSliceDelta(120)"), -1)
        self.assertEqual(run_interaction_logic(source, "dicomSliceDelta(-120)"), 1)


def run_interaction_logic(source: str, expression: str):
    if not source.strip():
        raise AssertionError("interaction-logic script is missing")
    program = """
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
    )
    return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
