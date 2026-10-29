"""Local batch validation of the mammo suspicious-form LLM prompt.

Reads archived mammography reports (radtracker/output/mammo_YYYYMM_reports.json),
selects those whose BI-RADS category (deterministic regex, same as the page) is
0/3/4/5, sends each report to the Claude Messages API with the SAME system prompt
and request settings used by tool/mammo-suspicious-form.html, and measures parse quality.

Usage:
    python radtracker/validate_mammo_form_llm.py --months 202602-202606 [--limit N] [--sleep SECONDS] [--model ID]

--model overrides the page's MODEL_ID (must be a key of CLAUDE_MODEL_SETTINGS), for comparing models.

API key: environment variable ANTHROPIC_API_KEY, otherwise ANTHROPIC_API_KEY=... in the
repo-root .env file, otherwise APIKey3 in ahk-scripts/radiologist_settings.ini.
Missing key -> exit code 2.

Privacy: report files contain chart numbers. Console output and the detail CSV
never contain chart_no, case_id or report text; only the report text itself is
sent to Claude (same as the page). Console output is ASCII only (cp950-safe).

Metrics printed at the end:
  - JSON-valid rate: model text parsed as JSON / reports processed.
  - Schema-valid rate (strict): the parsed object has a lesions array of objects
    (the page's validateParsed would accept it) AND no value had to be dropped by
    the enum whitelist (every lesion has a whitelisted type and side, and every
    non-null field/array item is whitelisted).
  - Lesion count distribution over structurally valid results.
  - Share of category-0 reports with >= 1 lesion (over structurally valid results).
  - Side consistency rate: see side_consistency().
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
HTML_REL = Path("tool") / "mammo-suspicious-form.html"
OUTPUT_REL = Path("radtracker") / "output"
API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2026-10-21"
FALLBACK_BETA = "server-side-fallback-2026-07-01"
INI_REL = Path("ahk-scripts") / "radiologist_settings.ini"

# Mirror of CLAUDE_MODEL_SETTINGS in tool/mammo-suspicious-form.html.
CLAUDE_MODEL_SETTINGS = {
    "claude-haiku-5-5": {"thinking": {"type": "disabled"}, "fallbacks": False},
    "claude-sonnet-5-5": {"thinking": {"type": "between_tools"}, "fallbacks": True},
    "claude-opus-5-5": {"thinking": None, "fallbacks": True},
}
SUSPICIOUS_CATEGORIES = (0, 3, 4, 5)
MAX_TRIES = 3

# Same pattern as CATEGORY_RE in the page (JS /i flag -> re.I; first match).
CATEGORY_RE = re.compile(r"(?:BI-?RADS\s*)?category\s*:?\s*(\d)([abc])?(?![a-z])", re.I)

# Mirror of ENUMS / SCALAR_FIELDS in tool/mammo-suspicious-form.html.
ENUMS = {
    "type": ["mass", "calcification", "asymmetry", "distortion", "skin_nipple",
             "axillary_ln", "ducts", "diffuse_skin", "other"],
    "side": ["R", "L", "multiple_unilateral", "multiple_bilateral"],
    "location": ["UOQ", "UIQ", "LOQ", "LIQ", "Subareolar", "Axillary tail"],
    "oneView": ["upper", "lower", "outer", "inner"],
    "size": ["<1", "1-2", "2-3", "3-4", ">4"],
    "shape": ["round", "oval", "lobular", "irregular"],
    "margin": ["circumscribed", "microlobulated", "obscured", "indistinct", "spiculated"],
    "density": ["high", "equal", "low", "fat"],
    "distribution": ["grouped", "linear", "segmental", "regional", "diffuse"],
    "morphology": ["amorphous", "coarse_heterogeneous", "fine_pleomorphic", "fine_linear_branching"],
    "asymmetryType": ["asymmetry", "focal", "developing"],
}
SCALAR_FIELDS = ["size", "shape", "margin", "density", "distribution", "morphology", "asymmetryType"]

CSV_FIELDS = ["month", "row_index", "regex_category", "json_ok", "schema_ok", "n_lesions",
              "types", "sides", "side_consistent", "dropped_values", "error"]


class ConfigError(Exception):
    """Raised when the HTML prompt or model id cannot be extracted."""


def say(msg: str = "") -> None:
    """Print ASCII-only text so the console never hits a cp950 encode error."""
    print(msg.encode("ascii", "replace").decode("ascii"), flush=True)


# ---------------------------------------------------------------------------
# Prompt / model id extraction (single prompt source shared with the page)
# ---------------------------------------------------------------------------
def extract_prompt_and_model(html: str) -> tuple[str, str]:
    """Return (MAMMO_SYSTEM_PROMPT, MODEL_ID) parsed from the page source."""
    start = html.find("/* MAMMO-PROMPT-START */")
    end = html.find("/* MAMMO-PROMPT-END */")
    if start < 0 or end < 0 or end < start:
        raise ConfigError("prompt markers not found")
    block = html[start:end]
    m = re.search(r"MAMMO_SYSTEM_PROMPT\s*=\s*`((?:\\.|[^`\\])*)`\s*;", block, re.S)
    if not m:
        raise ConfigError("MAMMO_SYSTEM_PROMPT template literal not found")
    raw = m.group(1)
    if "${" in raw.replace("\\${", ""):
        raise ConfigError("template interpolation in prompt is not supported")
    # Minimal template-literal unescape (\` \$ \\ and common escapes).
    prompt = re.sub(r"\\(.)", lambda e: {"n": "\n", "t": "\t"}.get(e.group(1), e.group(1)), raw, flags=re.S)
    mm = re.search(r"""const\s+MODEL_ID\s*=\s*(['"])([^'"]+)\1""", html)
    if not mm:
        raise ConfigError("MODEL_ID constant not found")
    return prompt, mm.group(2)


# ---------------------------------------------------------------------------
# Category, schema, side heuristics
# ---------------------------------------------------------------------------
def detect_category(text: str | None) -> tuple[int | None, str | None]:
    """Mirror of detectCategory(): (category, sub letter for 4 only)."""
    m = CATEGORY_RE.search(text or "")
    if not m:
        return None, None
    cat = int(m.group(1))
    sub = m.group(2).lower() if cat == 4 and m.group(2) else None
    return cat, sub


def validate_parsed(obj) -> tuple[dict | None, int]:
    """Mirror of the page's validateParsed().

    Returns (normalized, dropped). normalized is None when the structure is
    invalid (not an object, lesions not an array, or a lesion not an object).
    dropped counts values removed by the enum whitelist, including a missing
    or unknown type/side (the strict schema requires both).
    """
    if not isinstance(obj, dict) or not isinstance(obj.get("lesions"), list):
        return None, 0
    dropped = 0
    sub = obj.get("cat4Sub")
    if sub is not None and sub not in ("a", "b", "c"):
        dropped += 1
    out = {"cat4Sub": sub if sub in ("a", "b", "c") else None, "lesions": []}
    for les in obj["lesions"]:
        if not isinstance(les, dict):
            return None, 0
        lesion = {}
        for f in ("type", "side"):
            v = les.get(f)
            ok = isinstance(v, str) and v in ENUMS[f]
            lesion[f] = v if ok else None
            if not ok:
                dropped += 1
        for f in ("location", "oneView"):
            vals = les.get(f)
            kept: list[str] = []
            if isinstance(vals, list):
                for v in vals:
                    if isinstance(v, str) and v in ENUMS[f]:
                        if v not in kept:
                            kept.append(v)
                    else:
                        dropped += 1
            elif vals is not None:
                dropped += 1
            lesion[f] = kept
        ot = les.get("otherText")
        lesion["otherText"] = ot.strip() if isinstance(ot, str) and ot.strip() else None
        for f in SCALAR_FIELDS:
            v = les.get(f)
            ok = isinstance(v, str) and v in ENUMS[f]
            lesion[f] = v if ok else None
            if v is not None and not ok:
                dropped += 1
        out["lesions"].append(lesion)
    return out, dropped


_HEADER_LINE_RE = re.compile(r"^\s*(screening|diagnostic)\b.*\bmammograph|^\s*comparison\b|^\s*breast composition\b", re.I)
_RIGHT_RE = re.compile(r"\b(right|rt)\b", re.I)
_LEFT_RE = re.compile(r"\b(left|lt)\b", re.I)
_BOTH_RE = re.compile(r"\b(bilateral(ly)?|both\s+breasts?)\b", re.I)


def report_sides(text: str | None) -> set[str]:
    """Sides mentioned in the clinical part of the report.

    The exam header line ("Screening mammography of bilateral breast ..."),
    the comparison line and the breast-composition line are skipped because
    they mention sides without describing a finding. In the remaining text
    (Findings / Abnormalities / Recommended studies / IMP), "right"/"Rt"
    adds R, "left"/"Lt" adds L, "bilateral(ly)"/"both breast(s)" adds R and L.
    """
    lines = [ln for ln in (text or "").splitlines() if not _HEADER_LINE_RE.search(ln)]
    body = "\n".join(lines)
    sides: set[str] = set()
    if _RIGHT_RE.search(body):
        sides.add("R")
    if _LEFT_RE.search(body):
        sides.add("L")
    if _BOTH_RE.search(body):
        sides.update({"R", "L"})
    return sides


def lesion_sides(lesions: list[dict]) -> set[str]:
    """R -> {R}, L -> {L}, multiple_bilateral -> {R, L}; others add nothing."""
    out: set[str] = set()
    for les in lesions:
        side = les.get("side")
        if side in ("R", "L"):
            out.add(side)
        elif side == "multiple_bilateral":
            out.update({"R", "L"})
    return out


def side_consistency(text: str | None, lesions: list[dict]) -> bool | None:
    """Heuristic side check between report text and LLM lesions.

    Definition: consistent when every side implied by the lesions (see
    lesion_sides) is mentioned in the clinical part of the report (see
    report_sides). Returns None (not applicable, excluded from the rate) when
    there are no lesions, when no lesion carries a definite side
    (only multiple_unilateral / unknown), or when the report mentions no side.
    A report that also mentions a side only for a benign finding is still
    consistent, because only lesion sides missing from the text are counted
    as inconsistent.
    """
    if not lesions:
        return None
    ls = lesion_sides(lesions)
    rs = report_sides(text)
    if not ls or not rs:
        return None
    return ls <= rs


# ---------------------------------------------------------------------------
# Environment / IO helpers
# ---------------------------------------------------------------------------
def _ini_api_key(repo_root: Path) -> str | None:
    """APIKey3 from the AHK settings INI (UTF-16, written by AutoHotkey IniWrite)."""
    import configparser
    ini = repo_root / INI_REL
    if not ini.is_file():
        return None
    cp = configparser.ConfigParser(interpolation=None, strict=False)
    try:
        cp.read_string(ini.read_text(encoding="utf-16"))
    except (UnicodeError, configparser.Error):
        return None
    return (cp.get("AI", "APIKey3", fallback="") or "").strip() or None


def load_api_key(env: dict, repo_root: Path) -> str | None:
    key = (env.get("ANTHROPIC_API_KEY") or "").strip()
    if key:
        return key
    env_file = repo_root / ".env"
    if not env_file.is_file():
        return _ini_api_key(repo_root)
    for line in env_file.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        name, value = line.split("=", 1)
        if name.strip() == "ANTHROPIC_API_KEY":
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            if value.strip():
                return value.strip()
    return _ini_api_key(repo_root)


def parse_months(spec: str) -> list[str]:
    """'202602-202606' -> ['202602', ..., '202606']; also 'YYYYMM' or comma list."""
    months: list[str] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"(\d{4})(\d{2})(?:-(\d{4})(\d{2}))?", part)
        if not m:
            raise ValueError(f"bad month spec: {part}")
        y, mo = int(m.group(1)), int(m.group(2))
        if m.group(3):
            y2, mo2 = int(m.group(3)), int(m.group(4))
        else:
            y2, mo2 = y, mo
        if not (1 <= mo <= 12 and 1 <= mo2 <= 12) or (y, mo) > (y2, mo2):
            raise ValueError(f"bad month range: {part}")
        while (y, mo) <= (y2, mo2):
            months.append(f"{y:04d}{mo:02d}")
            mo += 1
            if mo > 12:
                y, mo = y + 1, 1
    return months


def urllib_post(url: str, headers: dict, body: bytes, timeout: float = 120.0) -> tuple[int, str]:
    """POST and return (status, body text). Network failure raises OSError."""
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            text = e.read().decode("utf-8", "replace")
        except Exception:
            text = ""
        return e.code, text


HttpPost = Callable[[str, dict, bytes, float], "tuple[int, str]"]


def build_request(prompt: str, report_text: str, model: str, api_key: str) -> tuple[dict, dict]:
    """Same (headers, body) as buildClaudeRequest() in the page, minus the browser-only CORS header."""
    settings = CLAUDE_MODEL_SETTINGS.get(model, {"thinking": None, "fallbacks": False})
    headers = {"content-type": "application/json", "x-api-key": api_key,
               "anthropic-version": ANTHROPIC_VERSION}
    body = {
        "model": model,
        "max_tokens": 8000,
        "system": prompt,
        "messages": [{"role": "user", "content": "MAMMOGRAPHY REPORT:\n" + report_text.strip()}],
        "output_config": {"effort": "low"},
    }
    if settings["thinking"]:
        body["thinking"] = settings["thinking"]
    if settings["fallbacks"]:
        headers["anthropic-beta"] = FALLBACK_BETA
        body["fallbacks"] = "default"
    return headers, body


_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.S | re.I)


def response_text(data: dict) -> str:
    """Mirror of claudeResponseText(): the ```json fenced block if any, else the outermost {...}."""
    blocks = data.get("content") or []
    text = "".join(b.get("text", "") for b in blocks
                   if isinstance(b, dict) and b.get("type") == "text").strip()
    m = _FENCE_RE.search(text)
    if m:
        return m.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    return text[start:end + 1] if start >= 0 and end > start else text


def call_claude(prompt: str, model: str, api_key: str, report_text: str,
                http_post: HttpPost, sleep: Callable[[float], None]) -> tuple[str | None, str | None]:
    """Return (model_text, error_code). Retries 429/5xx/network up to MAX_TRIES."""
    url = API_URL
    headers, req = build_request(prompt, report_text, model, api_key)
    body = json.dumps(req).encode("utf-8")
    err = None
    for attempt in range(1, MAX_TRIES + 1):
        try:
            status, text = http_post(url, headers, body, 120.0)
        except OSError as e:
            status, text, err = None, "", f"network_{type(e).__name__}"
        else:
            if status == 200:
                try:
                    data = json.loads(text)
                except ValueError:
                    return None, "bad_envelope"
                if not isinstance(data, dict) or not isinstance(data.get("content"), list):
                    return None, "bad_envelope"
                if data.get("stop_reason") == "refusal":
                    return None, "refusal"
                model_text = response_text(data)
                if not model_text:
                    return None, "empty_response"
                return model_text, None
            err = f"http_{status}"
            if not (status == 429 or 500 <= status < 600):
                return None, err
        if attempt < MAX_TRIES:
            sleep(2.0 * (2 ** (attempt - 1)))
    return None, err


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def evaluate_one(prompt, model, api_key, text, category, http_post, sleep) -> dict:
    row = {"json_ok": 0, "schema_ok": 0, "n_lesions": "", "types": "", "sides": "",
           "side_consistent": "", "dropped_values": "", "error": "", "_valid": None}
    model_text, err = call_claude(prompt, model, api_key, text, http_post, sleep)
    if err:
        row["error"] = err
        return row
    try:
        parsed = json.loads(model_text)
    except ValueError:
        row["error"] = "json_error"
        return row
    row["json_ok"] = 1
    valid, dropped = validate_parsed(parsed)
    if valid is None:
        row["error"] = "schema_error"
        return row
    row["_valid"] = valid
    row["dropped_values"] = dropped
    row["schema_ok"] = 1 if dropped == 0 else 0
    if dropped:
        row["error"] = "enum_dropped"
    lesions = valid["lesions"]
    row["n_lesions"] = len(lesions)
    row["types"] = "|".join(l["type"] or "?" for l in lesions)
    row["sides"] = "|".join(l["side"] or "?" for l in lesions)
    sc = side_consistency(text, lesions)
    row["side_consistent"] = "" if sc is None else int(sc)
    return row


def pct(n: int, d: int) -> str:
    return f"{n}/{d} ({100.0 * n / d:.1f}%)" if d else f"{n}/0 (n/a)"


def main(argv=None, *, repo_root: Path | None = None, env: dict | None = None,
         http_post: HttpPost | None = None, sleep: Callable[[float], None] = time.sleep,
         today: _dt.date | None = None) -> int:
    ap = argparse.ArgumentParser(description="Batch-validate the mammo suspicious-form LLM prompt.")
    ap.add_argument("--months", required=True, help="e.g. 202602-202606 (or 202602 / 202602,202604)")
    ap.add_argument("--limit", type=int, default=None, help="process at most N reports")
    ap.add_argument("--sleep", type=float, default=0.5, help="seconds between API calls (default 0.5)")
    ap.add_argument("--model", default=None, help="override the page MODEL_ID (a key of CLAUDE_MODEL_SETTINGS)")
    args = ap.parse_args(argv)

    repo_root = Path(repo_root) if repo_root else REPO_ROOT
    env = os.environ if env is None else env
    http_post = http_post or urllib_post

    api_key = load_api_key(env, repo_root)
    if not api_key:
        say("ERROR: Anthropic API key not found. Set environment variable ANTHROPIC_API_KEY,")
        say("       add ANTHROPIC_API_KEY=... to the repo-root .env file (gitignored),")
        say("       or set APIKey3 in ahk-scripts/radiologist_settings.ini.")
        return 2

    try:
        months = parse_months(args.months)
    except ValueError as e:
        say(f"ERROR: {e}")
        return 1
    try:
        html = (repo_root / HTML_REL).read_text(encoding="utf-8")
        prompt, model = extract_prompt_and_model(html)
    except (OSError, ConfigError) as e:
        say(f"ERROR: cannot read prompt from {HTML_REL.as_posix()}: {e}")
        return 1
    if args.model:
        if args.model not in CLAUDE_MODEL_SETTINGS:
            say(f"ERROR: unknown --model {args.model}; use one of {', '.join(CLAUDE_MODEL_SETTINGS)}")
            return 1
        model = args.model
    say(f"Model: {model} | prompt chars: {len(prompt)} | months: {', '.join(months)}")

    # Collect suspicious reports (only month, row index, category, text kept in memory).
    items = []
    out_dir = repo_root / OUTPUT_REL
    for month in months:
        path = out_dir / f"mammo_{month}_reports.json"
        if not path.is_file():
            say(f"WARN: {path.name} not found, skipped")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        reports = data.get("reports", []) if isinstance(data, dict) else data
        for idx, rep in enumerate(reports):
            text = rep.get("report_text") or ""
            cat, _sub = detect_category(text)
            if cat in SUSPICIOUS_CATEGORIES:
                items.append((month, idx, cat, text))
    if args.limit is not None:
        items = items[:max(args.limit, 0)]
    total = len(items)
    say(f"Selected {total} report(s) with category 0/3/4/5")
    if not total:
        return 1

    rows = []
    for i, (month, idx, cat, text) in enumerate(items, 1):
        if i > 1 and args.sleep > 0:
            sleep(args.sleep)
        row = evaluate_one(prompt, model, api_key, text, cat, http_post, sleep)
        row.update({"month": month, "row_index": idx, "regex_category": cat})
        rows.append(row)
        if row["schema_ok"]:
            status = f"ok lesions={row['n_lesions']}"
        elif row["_valid"] is not None:
            status = f"warn lesions={row['n_lesions']} dropped={row['dropped_values']}"
        else:
            status = f"FAIL {row['error']}"
        say(f"[{i}/{total}] {status}")

    stamp = (today or _dt.date.today()).strftime("%Y%m%d")
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"mammo_form_llm_validation_{stamp}.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # Metrics
    json_ok = sum(r["json_ok"] for r in rows)
    schema_ok = sum(r["schema_ok"] for r in rows)
    structural = [r for r in rows if r["_valid"] is not None]
    dist = Counter(r["n_lesions"] for r in structural)
    cat0 = [r for r in structural if r["regex_category"] == 0]
    cat0_hit = sum(1 for r in cat0 if r["n_lesions"] >= 1)
    sc_rows = [r for r in structural if r["side_consistent"] != ""]
    sc_ok = sum(1 for r in sc_rows if r["side_consistent"] == 1)
    errors = Counter(r["error"] for r in rows if r["error"])

    say("")
    say("=== Summary ===")
    say(f"Reports processed       : {total}")
    say(f"JSON-valid rate         : {pct(json_ok, total)}")
    say(f"Schema-valid rate       : {pct(schema_ok, total)}  (strict: no enum value dropped)")
    say("Lesion count distribution: " + (", ".join(f"{k}:{dist[k]}" for k in sorted(dist)) or "n/a"))
    say(f"Category 0 with >=1 lesion: {pct(cat0_hit, len(cat0))}")
    say(f"Side consistency rate   : {pct(sc_ok, len(sc_rows))}  (n/a rows excluded)")
    if errors:
        say("Errors: " + ", ".join(f"{k}={v}" for k, v in sorted(errors.items())))
    say(f"Detail CSV: {csv_path.relative_to(repo_root).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
