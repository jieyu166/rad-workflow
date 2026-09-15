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
import filecmp
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


IGNORE_DIRS = {"__pycache__", ".pytest_cache", ".ipynb_checkpoints"}
IGNORE_SUFFIX = {".pyc", ".pyo"}


def _skip(rel: Path) -> bool:
    """Build artifacts: never copied, never compared, never flagged as orphans."""
    return bool(IGNORE_DIRS & set(rel.parts)) or rel.suffix in IGNORE_SUFFIX


def stale_files(src: Path, dst: Path):
    """Files that differ between canonical and a copy, plus orphans in the copy.

    Name-only comparison is not enough: a skill can be refactored in place
    (e.g. 321-line SKILL.md -> 41-line router + references/) and the copy will
    still have the right folder name while serving stale content.
    """
    if not dst.exists():
        return ["<whole skill missing>"]
    bad = []
    want = set()
    for sp in src.rglob("*"):
        if sp.is_dir() or _skip(sp.relative_to(src)):
            continue
        rel = sp.relative_to(src).as_posix()
        want.add(rel)
        dp = dst / rel
        if not dp.exists():
            bad.append(f"missing:{rel}")
        elif not filecmp.cmp(sp, dp, shallow=False):
            bad.append(f"differs:{rel}")
    for dp in dst.rglob("*"):
        if dp.is_file() and not _skip(dp.relative_to(dst)):
            rel = dp.relative_to(dst).as_posix()
            if rel not in want:
                bad.append(f"orphan:{rel}")
    return bad


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
            missing = sorted(set(names) - have)
            extra = sorted(have - set(names))
            content = {}
            for d in src_skills:
                bad = stale_files(d, tgt / d.name)
                if bad:
                    content[d.name] = bad
            status = "OK" if not missing and not extra and not content else "DRIFT"
            if status == "DRIFT":
                drift = True
            print(f"  [{status}] {rel}  missing={missing} extra={extra}")
            for name, bad in sorted(content.items()):
                head = ", ".join(bad[:4]) + (f" (+{len(bad) - 4})" if len(bad) > 4 else "")
                print(f"      content drift: {name} -> {head}")
            continue
        # mirror in place (OneDrive-safe: no whole-tree rmtree, which hits locks)
        tgt.mkdir(parents=True, exist_ok=True)
        stale = 0
        for d in src_skills:
            shutil.copytree(d, tgt / d.name, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns(*IGNORE_DIRS, "*.pyc", "*.pyo"))
            # copytree never deletes: a refactor that drops files leaves stale
            # copies behind, so remove per-file what canonical no longer has.
            want = {p.relative_to(d).as_posix() for p in d.rglob("*")
                    if p.is_file() and not _skip(p.relative_to(d))}
            for dp in (tgt / d.name).rglob("*"):
                if not dp.is_file():
                    continue
                sub = dp.relative_to(tgt / d.name)
                if _skip(sub) or sub.as_posix() in want:
                    continue
                try:
                    dp.unlink()
                    stale += 1
                except OSError as e:
                    print(f"    (warn) could not remove stale {sub.as_posix()}: {e}")
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
              + (f", pruned {pruned}" if pruned else "")
              + (f", removed {stale} stale file(s)" if stale else "") + ")")

    if check and drift:
        sys.exit(2)
    if not check:
        print("Done. (.claude/.agents/.opencode copies are gitignored; commit only skills/)")


if __name__ == "__main__":
    main()
