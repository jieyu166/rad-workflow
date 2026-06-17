#!/usr/bin/env python3
"""Evaluate the ct_chest.md prompt against real chest CT reports.

Pipeline (hybrid comparison):
  1. parse each fetched report -> impression (input) + truth findings (9 systems)
  2. reproduce the AHK I2F call: ct_chest.md system prompt (placeholders filled
     per contrast flag, exactly as US.ahk does) + "Impression:\n<impression>"
     -> gpt-5.4-mini -> generated findings
  3. structural diff per system: missing / extra / misplaced bullets + DDx residue
  4. LLM-judge ONLY the flagged diffs: real discrepancy vs harmless rephrasing
  5. aggregate error patterns -> ct_chest_eval_<scope>.json + console summary

Faithful to US.ahk I2F_DoGenerate: model gpt-5.4-mini, chat/completions, no
temperature, system=ct_chest.md (only {{ctMethod}}/{{ctContrastNote}}/
{{ctLimitationNote}} substituted; {{indication_or_placeholder}}/{{comparison_line}}
left as-is, as the AHK does).

Comparison ignores the scaffold header (METHOD/INDICATION/Comparison) — those are
filled by HIS, not the AI — and compares only the "Imaging findings :" body.

Must run on a network that can reach api.openai.com. Output is gitignored.
"""

import argparse
import configparser
import difflib
import json
import re
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
PROMPT_PATH = BASE_DIR.parent / "ahk-scripts" / "prompts" / "ct_chest.md"
SETTINGS_PATH = BASE_DIR.parent / "ahk-scripts" / "radiologist_settings.ini"

ENDPOINT = "https://api.openai.com/v1/chat/completions"
MODEL = "gpt-5.4-mini"

SPLIT_MARK = "Other details are mentioned as followings:"
FINDINGS_MARK = "Imaging findings :"
SECTION_RE = re.compile(r"^\s*(\d)\.\s*(.+?)\s*:\s*$")
DDX_RE = re.compile(
    r"\b(ddx|differential|suspect|suspected|favor|probably|compatible with|"
    r"consistent with|suggest|could be|may represent|cannot exclude|r/o|rule out)\b",
    re.IGNORECASE,
)

# AHK placeholder fills (US.ahk I2F_DoGenerate)
CONTRAST_FILL = {
    "ctMethod": "METHOD: (1) HRCT (2) Noncontrast survey (3) contrast enhancement were performed",
    "ctContrastNote": "Before and after the administration of intravenous contrast there was no adverse effect.",
    "ctLimitationNote": "",
}
NONCONTRAST_FILL = {
    "ctMethod": "METHOD: (1) HRCT (2) Noncontrast survey were performed",
    "ctContrastNote": "",
    "ctLimitationNote": "*This is a Non contrast medium injection image.\nLimited evaluation for lymphadenopathy, vascular structure, soft tissue density organs and soft tissue lesions survey;",
}


def read_api_key() -> str:
    for enc in ("utf-8-sig", "utf-16", "cp950"):
        cfg = configparser.ConfigParser()
        try:
            cfg.read(SETTINGS_PATH, encoding=enc)
        except UnicodeError:
            continue
        if cfg.has_option("AI", "APIKey"):
            key = cfg.get("AI", "APIKey").strip()
            if key:
                return key
    raise SystemExit("OpenAI API key not found in [AI] APIKey of radiologist_settings.ini")


def build_system_prompt(contrast: bool) -> str:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    fill = CONTRAST_FILL if contrast else NONCONTRAST_FILL
    for k, v in fill.items():
        text = text.replace("{{" + k + "}}", v)
    return text


SCAFFOLD_MARK = "CT study of the thorax was performed"


def parse_report(text: str) -> dict | None:
    if not text or "Impression:" not in text or FINDINGS_MARK not in text:
        return None
    after_imp = text.split("Impression:", 1)[1]
    # impression ends at the scaffold start; markers tried in order of preference
    end = len(after_imp)
    for mark in (SPLIT_MARK, SCAFFOLD_MARK, FINDINGS_MARK):
        idx = after_imp.find(mark)
        if idx != -1:
            end = min(end, idx)
    imp = after_imp[:end].strip()
    findings_block = text.split(FINDINGS_MARK, 1)[1].strip()
    return {"impression": imp, "truth_findings": findings_block}


def parse_sections(findings_block: str) -> dict:
    """Return {section_label: [bullet, ...]} from a 9-system findings body."""
    sections: dict[str, list[str]] = {}
    current = None
    buf: list[str] = []

    def flush():
        if current is not None:
            sections[current] = [b.strip() for b in buf if b.strip()]

    for raw in findings_block.splitlines():
        m = SECTION_RE.match(raw)
        if m:
            flush()
            current = f"{m.group(1)}. {m.group(2).strip()}"
            buf = []
            continue
        line = raw.strip()
        if line.startswith("- "):
            buf.append(line[2:].strip())
        elif line.startswith("*") or line.lower().startswith("limited eval"):
            continue  # scaffold limitation note
        elif line and buf:
            buf[-1] = (buf[-1] + " " + line).strip()  # continuation of prev bullet
    flush()
    return sections


def _norm(s: str) -> str:
    s = re.sub(r"\(srs/img[^)]*\)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\(arrows[^)]*\)", "", s, flags=re.IGNORECASE)
    s = re.sub(r"[^a-z0-9 ]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def _best_ratio(b: str, candidates: list[str]) -> float:
    nb = _norm(b)
    best = 0.0
    for c in candidates:
        r = difflib.SequenceMatcher(None, nb, _norm(c)).ratio()
        best = max(best, r)
    return best


def structural_diff(gen: dict, truth: dict, match_thr: float = 0.72) -> list[dict]:
    flags = []
    all_secs = list(dict.fromkeys(list(truth) + list(gen)))
    gen_all = [b for v in gen.values() for b in v]

    for sec in all_secs:
        tb = truth.get(sec, [])
        gb = gen.get(sec, [])
        for b in tb:
            if _best_ratio(b, gb) < match_thr:
                # present in truth section but not in same gen section
                kind = "misplaced" if _best_ratio(b, gen_all) >= match_thr else "missing"
                flags.append({"type": kind, "section": sec, "bullet": b})
        for b in gb:
            tb_all = [x for v in truth.values() for x in v]
            if _best_ratio(b, tb_all) < match_thr:
                flags.append({"type": "extra", "section": sec, "bullet": b})
            if DDX_RE.search(b):
                flags.append({"type": "ddx_residue", "section": sec, "bullet": b})
    return flags


def call_gpt(api_key: str, system: str, user: str, timeout: int = 90) -> str | None:
    payload = {"model": MODEL, "messages": [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]}
    try:
        r = requests.post(ENDPOINT, headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"    GPT error: {e}")
        return None


JUDGE_SYSTEM = (
    "You audit a radiology prompt that converts a CT-chest IMPRESSION into descriptive "
    "FINDINGS. You get the IMPRESSION (the prompt's input), the model-GENERATED findings, "
    "the radiologist's REAL findings, and auto-flagged differences. Classify EACH flag into "
    "exactly one category, using the IMPRESSION as ground truth for what the prompt had to "
    "work with:\n"
    "  prompt_dropped     - item is in IMPRESSION and in REAL, but GENERATED omitted it\n"
    "  prompt_kept_ddx    - GENERATED kept DDx/suspect/favor/'compatible with'/follow-up wording the prompt should strip\n"
    "  prompt_misplaced   - GENERATED put the finding under the wrong numbered system vs REAL\n"
    "  prompt_hallucinated- GENERATED text is NOT in the IMPRESSION at all (true invention)\n"
    "  editorial          - GENERATED item IS in the IMPRESSION but the radiologist chose to drop/alter it (NOT a prompt error)\n"
    "  doctor_added       - REAL item is NOT in the IMPRESSION (radiologist added from images; prompt could not produce it)\n"
    "  false_flag         - same finding, only rephrasing/ordering/whitespace differs (NOT an error)\n"
    "is_prompt_error=true ONLY for prompt_dropped, prompt_kept_ddx, prompt_misplaced, prompt_hallucinated. "
    "Return strict JSON: {\"verdicts\":[{\"bullet\":str,\"type\":str,\"category\":str,"
    "\"is_prompt_error\":bool,\"reason\":str}],\"summary\":str}."
)


def judge(api_key: str, impression: str, gen_block: str, truth_block: str, flags: list[dict]) -> dict | None:
    if not flags:
        return {"verdicts": [], "summary": "no structural flags"}
    user = (
        f"IMPRESSION (input):\n{impression}\n\nGENERATED FINDINGS:\n{gen_block}\n\n"
        f"REAL FINDINGS:\n{truth_block}\n\nAUTO-FLAGS:\n{json.dumps(flags, ensure_ascii=False)}"
    )
    out = call_gpt(api_key, JUDGE_SYSTEM, user)
    if not out:
        return None
    m = re.search(r"\{.*\}", out, re.DOTALL)
    try:
        return json.loads(m.group(0)) if m else None
    except json.JSONDecodeError:
        return None


def extract_findings_body(gen_text: str) -> str:
    """Pull the Imaging findings body out of the model output."""
    if FINDINGS_MARK in gen_text:
        return gen_text.split(FINDINGS_MARK, 1)[1].strip()
    return gen_text.strip()


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate ct_chest.md against real reports.")
    ap.add_argument("--scope", default="sample30")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--no-judge", action="store_true")
    args = ap.parse_args()

    reports_file = OUTPUT_DIR / f"ct_chest_{args.scope}_reports.json"
    data = json.loads(reports_file.read_text(encoding="utf-8"))
    api_key = read_api_key()

    rows = [r for r in data["reports"] if r.get("status") == "fetched" and r.get("report_text")]
    if args.limit:
        rows = rows[:args.limit]
    print(f"evaluating {len(rows)} report(s) with {MODEL}...")

    results = []
    cats = ["prompt_dropped", "prompt_kept_ddx", "prompt_misplaced",
            "prompt_hallucinated", "editorial", "doctor_added", "false_flag"]
    agg = {c: 0 for c in cats}
    agg.update({"prompt_error_total": 0, "cases_clean": 0, "cases_prompt_clean": 0})

    for i, r in enumerate(rows, 1):
        parsed = parse_report(r["report_text"])
        if not parsed:
            print(f"  [{i}] {r['case_id']} parse_failed")
            continue
        system = build_system_prompt(bool(r.get("contrast")))
        user = "Impression:\n" + parsed["impression"]
        gen_text = call_gpt(api_key, system, user)
        if gen_text is None:
            continue

        gen_body = extract_findings_body(gen_text)
        gen_sec = parse_sections(gen_body)
        truth_sec = parse_sections(parsed["truth_findings"])
        flags = structural_diff(gen_sec, truth_sec)

        verdicts = None
        if not args.no_judge:
            verdicts = judge(api_key, parsed["impression"], gen_body, parsed["truth_findings"], flags)

        prompt_errs = []
        if verdicts and verdicts.get("verdicts"):
            for v in verdicts["verdicts"]:
                cat = v.get("category", "false_flag")
                if cat in agg:
                    agg[cat] += 1
                if v.get("is_prompt_error"):
                    prompt_errs.append(v)
        agg["prompt_error_total"] += len(prompt_errs)
        if not flags:
            agg["cases_clean"] += 1
        if not prompt_errs:
            agg["cases_prompt_clean"] += 1

        results.append({
            "case_id": r["case_id"],
            "contrast": r.get("contrast"),
            "flags": flags,
            "judge": verdicts,
            "prompt_errors": prompt_errs,
            "gen_findings": gen_body,
            "truth_findings": parsed["truth_findings"],
            "impression": parsed["impression"],
        })
        tag = "prompt-clean" if not prompt_errs else f"{len(prompt_errs)} prompt-error(s)"
        print(f"  [{i}/{len(rows)}] {r['case_id']} ({'C' if r.get('contrast') else 'N'}): "
              f"{len(flags)} flag(s) -> {tag}")

    out = {"scope": args.scope, "model": MODEL, "n": len(results),
           "aggregate": agg, "results": results}
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"ct_chest_eval_{args.scope}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== aggregate ===")
    print(f"  cases evaluated      : {len(results)}")
    print(f"  prompt-clean cases   : {agg['cases_prompt_clean']}/{len(results)}")
    print("  -- prompt errors --")
    print(f"  dropped              : {agg['prompt_dropped']}")
    print(f"  kept DDx             : {agg['prompt_kept_ddx']}")
    print(f"  misplaced            : {agg['prompt_misplaced']}")
    print(f"  hallucinated         : {agg['prompt_hallucinated']}")
    print(f"  >> prompt_error_total: {agg['prompt_error_total']}")
    print("  -- not prompt errors --")
    print(f"  editorial            : {agg['editorial']}")
    print(f"  doctor_added         : {agg['doctor_added']}")
    print(f"  false_flag           : {agg['false_flag']}")
    print(f"  -> {out_path}")


if __name__ == "__main__":
    main()
