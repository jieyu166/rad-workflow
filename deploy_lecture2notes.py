#!/usr/bin/env python3
"""Deploy the vendored lecture2notes product and this repository's overlay.

Two jobs, one script, because they are two halves of one answer to "is the
lecture pipeline on this machine the one this repository describes?":

* Without flags it installs the pinned submodule, lets ``l2n`` deploy its skill
  to the three agent directories, copies the five overlay files into the user's
  home, and prints the settings that actually took effect.
* With ``--check`` it writes nothing and reports drift instead, so the question
  can be asked without changing the answer.

Three decisions here are load-bearing:

* **The overlay is copied file by file, never as a directory sync.** The home
  overlay directory is the user's own; a sync would delete whatever else they
  keep there, and a deployment tool that eats unrelated files is worse than one
  that never ran.
* **``l2n`` is resolved with :func:`shutil.which` and then called by its
  resolved path.** On Windows a bare name is looked up as ``name.exe`` only, so
  calling ``l2n`` directly would miss the shim a pip install actually writes.
* **``--check`` recomputes both sides from disk.** Comparing against anything
  recorded at install time would report "ok" for a file somebody has edited,
  which is the one case the check exists for.

Console output stays inside cp950: this repository is driven from a cp950
console, where a decorative character is a crash rather than a cosmetic issue.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parent

#: The pinned product. Not under ``skills/``, so ``sync_skills.py`` does not
#: enumerate it as one more skill to distribute.
SUBMODULE_RELATIVE = "vendor/lecture2notes"
SUBMODULE_PATH = REPO_ROOT / "vendor" / "lecture2notes"

#: The canonical copy of the personal overlay, which is what this repository
#: version-controls; the copy in the home directory is the deployed artefact.
OVERLAY_SOURCE = REPO_ROOT / "skills-overlay" / "lecture2notes"

#: The directory name lecture2notes reads the user overlay from.
OVERLAY_DIR_NAME = ".lecture2notes"

#: Exactly the files an overlay may contain, in deployment order.
OVERLAY_FILES: Tuple[str, ...] = (
    "note.frontmatter.yaml",
    "note.template.md",
    "corrections.json",
    "outputs.toml",
    "privacy.toml",
)

#: The command that performs the editable install. A list rather than a string
#: so the running interpreter is the one that installs, and so a test can point
#: it at a recorder instead of really installing anything.
PIP_COMMAND: List[str] = [sys.executable, "-m", "pip"]

#: The CLI the product installs.
L2N_NAME = "l2n"

#: The keys reported after a deployment, in reading order.
REPORTED_KEYS: Tuple[str, ...] = ("profile", "note.style", "pbf")

TOTAL_STEPS = 5

EXIT_OK = 0
#: Drift, or a precondition that is not met.
EXIT_PROBLEM = 2
#: The product's CLI is not on PATH.
EXIT_NO_L2N = 3

INIT_HINT = "run: git submodule update --init " + SUBMODULE_RELATIVE
INSTALL_HINT = "run: python deploy_lecture2notes.py  (安裝 lecture2notes 後才會有 l2n)"


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------
def say(text: str = "") -> None:
    """Print one line, degrading rather than crashing on a narrow console."""
    stream = sys.stdout
    try:
        stream.write(text + "\n")
    except UnicodeEncodeError:  # pragma: no cover - console-dependent
        encoding = getattr(stream, "encoding", None) or "ascii"
        safe = text.encode(encoding, "backslashreplace").decode(encoding, "replace")
        stream.write(safe + "\n")
    stream.flush()


def step(number: int, text: str) -> None:
    say("[step %d/%d] %s" % (number, TOTAL_STEPS, text))


def ok(text: str) -> None:
    say("[ok] %s" % text)


def warn(text: str) -> None:
    say("[warn] %s" % text)


def error(text: str) -> None:
    say("[error] %s" % text)


def drift(text: str) -> None:
    say("[drift] %s" % text)


def _tail(text: str, limit: int = 12) -> List[str]:
    """The last few non-empty lines of a captured stream, for a failure report."""
    lines = [line.rstrip() for line in (text or "").splitlines() if line.strip()]
    return lines[-limit:]


# --------------------------------------------------------------------------
# environment
# --------------------------------------------------------------------------
def resolve_home(raw: Optional[str] = None) -> Path:
    """The home directory every step works against."""
    if raw:
        return Path(raw).expanduser().resolve()
    return Path.home()


def child_env(home: Path) -> Dict[str, str]:
    """The environment child processes see.

    ``HOME`` and ``USERPROFILE`` are both set because the product reads the home
    directory through ``Path.home()``, which consults ``USERPROFILE`` on Windows
    and ``HOME`` elsewhere. ``PYTHONIOENCODING`` is pinned so the output this
    script captures through a pipe decodes the same way on every console.
    """
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["USERPROFILE"] = str(home)
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run(argv: Sequence[str], env: Optional[Dict[str, str]] = None):
    """Run a command, capturing both streams as UTF-8 text."""
    return subprocess.run(
        list(argv),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def find_l2n() -> Optional[str]:
    """The resolved path of the product's CLI, or None when it is not on PATH."""
    return shutil.which(L2N_NAME)


# --------------------------------------------------------------------------
# submodule
# --------------------------------------------------------------------------
def submodule_is_initialised(path: Path) -> bool:
    """A submodule nobody has run ``git submodule update`` for is an empty dir."""
    if not path.is_dir():
        return False
    return any(path.iterdir())


def submodule_tag(path: Path) -> Optional[str]:
    """The tag the submodule sits exactly on, or None."""
    try:
        result = run(["git", "-C", str(path), "describe", "--tags", "--exact-match"])
    except OSError:  # pragma: no cover - git missing
        return None
    if result.returncode != 0:
        return None
    tag = (result.stdout or "").strip()
    return tag or None


def submodule_commit(path: Path) -> str:
    """The submodule's short HEAD, for the message that says it is not on a tag."""
    try:
        result = run(["git", "-C", str(path), "rev-parse", "--short", "HEAD"])
    except OSError:  # pragma: no cover - git missing
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    return (result.stdout or "").strip() or "unknown"


# --------------------------------------------------------------------------
# overlay
# --------------------------------------------------------------------------
def overlay_target(home: Path) -> Path:
    return Path(home) / OVERLAY_DIR_NAME


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def locally_edited(home: Path) -> List[str]:
    """Overlay files whose deployed copy differs from the source. Writes nothing.

    The repository is the source and the home copy is the artefact, so a deploy
    is right to overwrite -- but an edit made directly in the home copy is about
    to be discarded, and discarding it without a word is how one gets lost.
    """
    destination = overlay_target(home)
    edited: List[str] = []
    for name in OVERLAY_FILES:
        source = OVERLAY_SOURCE / name
        deployed = destination / name
        if not source.is_file() or not deployed.is_file():
            continue
        try:
            if sha256_of(source) != sha256_of(deployed):
                edited.append(name)
        except OSError:  # unreadable here is the copy step's finding to report
            continue
    return edited


def copy_overlay(home: Path) -> List[str]:
    """Copy the five overlay files into *home*. Returns one line per failure.

    Every file is attempted even after one fails, so a single locked file does
    not hide the state of the other four, and what did copy stays copied: the
    operation is idempotent, so rerunning finishes the job.
    """
    destination = overlay_target(home)
    try:
        destination.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return ["%s: cannot be created (%s)" % (destination, exc)]
    failures: List[str] = []
    for name in OVERLAY_FILES:
        source = OVERLAY_SOURCE / name
        if not source.is_file():
            failures.append("%s: missing from %s" % (name, OVERLAY_SOURCE))
            continue
        try:
            shutil.copyfile(source, destination / name)
        except OSError as exc:
            failures.append("%s: %s" % (name, exc))
    return failures


def compare_overlay(home: Path) -> List[str]:
    """One line per overlay file that is missing or differs. Writes nothing."""
    destination = overlay_target(home)
    problems: List[str] = []
    for name in OVERLAY_FILES:
        source = OVERLAY_SOURCE / name
        deployed = destination / name
        if not source.is_file():
            problems.append("%s: missing from %s" % (name, OVERLAY_SOURCE))
            continue
        if not deployed.is_file():
            problems.append("%s: missing from %s" % (name, destination))
            continue
        if sha256_of(source) != sha256_of(deployed):
            problems.append("%s: differs from %s" % (name, source))
    return problems


# --------------------------------------------------------------------------
# reporting the effective settings
# --------------------------------------------------------------------------
def _format_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value)


def report_settings(l2n: str, home: Path) -> Optional[str]:
    """Print profile, note.style and pbf with their layers. None when fine."""
    result = run([l2n, "profile", "show", "--json"], env=child_env(home))
    if result.returncode != 0:
        for line in _tail(result.stderr) or _tail(result.stdout):
            say("  " + line)
        return "l2n profile show 失敗（exit %d）" % result.returncode
    try:
        data = json.loads(result.stdout)
    except ValueError as exc:
        return "l2n profile show 沒有回傳 JSON（%s）" % exc
    if not isinstance(data, dict):
        return "l2n profile show 回傳的不是 JSON 物件"
    missing = [key for key in REPORTED_KEYS if key not in data]
    if missing:
        return "l2n profile show 沒有回報：%s" % ", ".join(missing)
    for key in REPORTED_KEYS:
        entry = data[key]
        say("  %s = %s  (%s)"
            % (key, _format_value(entry.get("value")), entry.get("source")))
    return None


# --------------------------------------------------------------------------
# the two commands
# --------------------------------------------------------------------------
def deploy(home: Path) -> int:
    step(1, "檢查 submodule %s" % SUBMODULE_RELATIVE)
    if not submodule_is_initialised(SUBMODULE_PATH):
        error("%s 尚未初始化" % SUBMODULE_RELATIVE)
        say(INIT_HINT)
        return EXIT_PROBLEM
    tag = submodule_tag(SUBMODULE_PATH)
    if tag:
        ok("submodule 位於 %s" % tag)
    else:
        warn("submodule 不在任何 tag 上，目前 commit %s"
             % submodule_commit(SUBMODULE_PATH))

    step(2, "以 %s 做 editable 安裝" % Path(sys.executable).name)
    install = run(list(PIP_COMMAND) + ["install", "-e", str(SUBMODULE_PATH)])
    if install.returncode != 0:
        for line in _tail(install.stderr) or _tail(install.stdout):
            say("  " + line)
        error("editable 安裝失敗（exit %d）" % install.returncode)
        return EXIT_PROBLEM
    ok("editable 安裝完成")

    l2n = find_l2n()
    if l2n is None:
        error("安裝後仍找不到 %s" % L2N_NAME)
        say(INSTALL_HINT)
        return EXIT_NO_L2N

    step(3, "部署 skill 到三家 agent 目錄")
    skill = run([l2n, "install-skill", "--all"], env=child_env(home))
    for line in _tail(skill.stdout, 8):
        say("  " + line)
    if skill.returncode != 0:
        for line in _tail(skill.stderr):
            say("  " + line)
        error("l2n install-skill --all 失敗（exit %d）" % skill.returncode)
        return EXIT_PROBLEM
    ok("skill 已部署")

    step(4, "複製 overlay 到 %s" % overlay_target(home))
    for name in locally_edited(home):
        warn("overlay %s 與版控內容不同，本次複製會覆蓋掉；"
             "要保留請改 skills-overlay/lecture2notes/ 再重跑" % name)
    failures = copy_overlay(home)
    for line in failures:
        error(line)
    if failures:
        error("overlay 複製未完成；已複製的檔保留，重跑即可")
        return EXIT_PROBLEM
    ok("overlay 五個檔已就位")

    step(5, "回報生效設定")
    problem = report_settings(l2n, home)
    if problem is not None:
        error(problem)
        return EXIT_PROBLEM
    ok("部署完成")
    return EXIT_OK


def check(home: Path) -> int:
    l2n = find_l2n()
    if l2n is None:
        error("%s 不在 PATH 上" % L2N_NAME)
        say(INSTALL_HINT)
        return EXIT_NO_L2N

    skill = run([l2n, "install-skill", "--check", "--all"], env=child_env(home))
    for line in _tail(skill.stdout, 32):
        say(line)
    if skill.returncode != 0:
        for line in _tail(skill.stderr):
            say(line)

    problems = compare_overlay(home)
    for line in problems:
        drift(line)

    if problems or skill.returncode != 0:
        error("有 drift：重跑 python deploy_lecture2notes.py 可修復")
        return EXIT_PROBLEM
    ok("skill 與 overlay 都與版控內容一致")
    return EXIT_OK


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deploy_lecture2notes.py",
        description="部署 vendor/lecture2notes 與 skills-overlay/lecture2notes",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="只比對不寫檔；一致 exit 0，有 drift exit 2，缺 l2n exit 3",
    )
    parser.add_argument(
        "--home",
        default=None,
        help="改用這個路徑當家目錄（測試用）",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    home = resolve_home(args.home)
    if args.check:
        return check(home)
    return deploy(home)


if __name__ == "__main__":
    sys.exit(main())
