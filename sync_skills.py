#!/usr/bin/env python3
"""Sync the canonical skills/ library to each AI agent's project skills folder.

Why this exists (no-symlink design):
  The project lives in OneDrive, which corrupts symlinks (uploads them as real
  files -> break on other machines). So instead of symlinking three agent
  folders to one shared dir, we keep ONE canonical source (skills/, tracked in
  Git -> synced across machines via GitHub) and COPY it into each agent's
  project folder. The copies are gitignored (derived artifacts).

Agent project skill paths:
  - Claude Code : .claude/skills/
  - OpenAI Codex: .agents/skills/   (note the plural 's')
  - OpenCode    : reads .claude/skills/ AND .agents/skills/ natively
                  (per https://opencode.ai/docs/skills/) -> covered for free.
                  Also mirrored to .opencode/skills/ for its native path.

Usage:
  python sync_skills.py          # mirror skills/ -> all agent folders
  python sync_skills.py --check  # report drift without writing

Edit skills ONLY in skills/<name>/SKILL.md, then run this to distribute.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "skills"
TARGETS = [
    ROOT / ".claude" / "skills",    # Claude Code
    ROOT / ".agents" / "skills",    # OpenAI Codex (plural 's')
    ROOT / ".opencode" / "skills",  # OpenCode native path
]


def iter_skill_dirs(base: Path):
    if not base.exists():
        return []
    return sorted(d for d in base.iterdir() if d.is_dir() and (d / "SKILL.md").exists())


def main():
    check = "--check" in sys.argv
    if not SRC.exists():
        print(f"ERROR: canonical {SRC} not found. Create skills/<name>/SKILL.md first.", file=sys.stderr)
        sys.exit(1)
    src_skills = iter_skill_dirs(SRC)
    if not src_skills:
        print(f"ERROR: no skills (with SKILL.md) under {SRC}.", file=sys.stderr)
        sys.exit(1)
    names = [d.name for d in src_skills]
    print(f"Canonical skills/ : {len(names)} skill(s) -> {', '.join(names)}")

    drift = False
    for tgt in TARGETS:
        rel = tgt.relative_to(ROOT)
        if check:
            have = {d.name for d in iter_skill_dirs(tgt)}
            missing = set(names) - have
            extra = have - set(names)
            status = "OK" if not missing and not extra else "DRIFT"
            if status == "DRIFT":
                drift = True
            print(f"  [{status}] {rel}  missing={sorted(missing)} extra={sorted(extra)}")
            continue
        # mirror in place (OneDrive-safe: no whole-tree rmtree, which hits locks)
        tgt.mkdir(parents=True, exist_ok=True)
        for d in src_skills:
            shutil.copytree(d, tgt / d.name, dirs_exist_ok=True)
        # prune skills no longer in canonical (best-effort; tolerate OneDrive locks)
        pruned = 0
        for d in iter_skill_dirs(tgt):
            if d.name not in names:
                try:
                    shutil.rmtree(d)
                    pruned += 1
                except OSError as e:
                    print(f"    (warn) could not prune {d.name}: {e}")
        print(f"  synced -> {rel}  ({len(names)} skills"
              + (f", pruned {pruned}" if pruned else "") + ")")

    if check and drift:
        sys.exit(2)
    if not check:
        print("Done. (.claude/.agents/.opencode copies are gitignored; commit only skills/)")


if __name__ == "__main__":
    main()
