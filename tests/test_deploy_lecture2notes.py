"""Tests for deploy_lecture2notes.py.

Nothing here installs anything or touches the real home directory. Two stub
executables stand in for the commands the script drives:

* a stub ``pip``, injected by repointing ``PIP_COMMAND``, and
* a stub ``l2n`` written onto ``PATH``, so the script's own ``shutil.which``
  lookup is exercised rather than bypassed.

Both append one JSON line to the same log file, which is what makes the order
of the steps assertable rather than inferred. The log lives outside the
temporary home, because one test asserts that ``--check`` leaves every file in
that home untouched.
"""

import json
import os
import stat
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import deploy_lecture2notes as deploy  # noqa: E402

#: What the stub l2n answers `profile show --json` with.
PROFILE_JSON = {
    "profile": {"value": "radiology", "source": "user"},
    "note.style": {"value": "faithful", "source": "user"},
    "pbf": {"value": True, "source": "user"},
}

STUB_BODY = '''\
import json, os, sys

log = os.environ.get("STUB_LOG")
if log:
    with open(log, "a", encoding="utf-8") as handle:
        handle.write(json.dumps({"tool": %(tool)r, "args": sys.argv[1:]}) + "\\n")

args = sys.argv[1:]
if args[:1] == ["profile"]:
    sys.stdout.write(json.dumps(%(profile)s))
else:
    sys.stdout.write("[ok] stub %(tool)s\\n")
sys.exit(int(os.environ.get("%(exit_var)s", "0")))
'''


def _write_stub(path, tool, exit_var):
    path.write_text(
        STUB_BODY % {
            "tool": tool,
            "profile": repr(PROFILE_JSON),
            "exit_var": exit_var,
        },
        encoding="utf-8",
    )


def _write_launcher(bin_dir, name, script):
    """A PATH-visible launcher for *script*, in this platform's shape."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        launcher = bin_dir / (name + ".cmd")
        launcher.write_text(
            '@echo off\r\n"%s" "%s" %%*\r\nexit /b %%ERRORLEVEL%%\r\n'
            % (sys.executable, script),
            encoding="utf-8",
        )
    else:
        launcher = bin_dir / name
        launcher.write_text(
            '#!/bin/sh\nexec "%s" "%s" "$@"\n' % (sys.executable, script),
            encoding="utf-8",
        )
        launcher.chmod(launcher.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)
    return launcher


class Harness:
    """Everything one test needs: a home, a submodule, two stubs and a log."""

    def __init__(self, tmp_path, monkeypatch):
        self.tmp_path = tmp_path
        self.monkeypatch = monkeypatch
        self.home = tmp_path / "home"
        self.home.mkdir()
        self.log = tmp_path / "stub-calls.log"
        self.submodule = tmp_path / "vendor" / "lecture2notes"
        self.submodule.mkdir(parents=True)
        (self.submodule / "pyproject.toml").write_text("[project]\n", encoding="utf-8")

        bin_dir = tmp_path / "bin"
        _write_stub(tmp_path / "stub_l2n.py", "l2n", "L2N_STUB_EXIT")
        _write_stub(tmp_path / "stub_pip.py", "pip", "PIP_STUB_EXIT")
        _write_launcher(bin_dir, "l2n", tmp_path / "stub_l2n.py")
        self.bin_dir = bin_dir

        monkeypatch.setattr(deploy, "SUBMODULE_PATH", self.submodule)
        monkeypatch.setattr(
            deploy, "PIP_COMMAND", [sys.executable, str(tmp_path / "stub_pip.py")]
        )
        monkeypatch.setenv("STUB_LOG", str(self.log))
        monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])

    # -- driving ---------------------------------------------------------
    def deploy(self):
        return deploy.main(["--home", str(self.home)])

    def check(self):
        return deploy.main(["--check", "--home", str(self.home)])

    def hide_l2n(self):
        self.monkeypatch.setenv("PATH", str(self.tmp_path / "empty-bin"))

    # -- reading back ----------------------------------------------------
    def calls(self):
        if not self.log.is_file():
            return []
        return [
            json.loads(line)
            for line in self.log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def overlay_dir(self):
        return self.home / deploy.OVERLAY_DIR_NAME

    def snapshot(self):
        """Every file under the home, with its size and mtime in nanoseconds."""
        entries = {}
        for path in sorted(self.home.rglob("*")):
            info = path.stat()
            entries[str(path.relative_to(self.home))] = (
                path.is_dir(),
                info.st_size,
                info.st_mtime_ns,
            )
        return entries


@pytest.fixture
def harness(tmp_path, monkeypatch):
    return Harness(tmp_path, monkeypatch)


# --------------------------------------------------------------------------
# constants
# --------------------------------------------------------------------------
def test_submodule_constant_is_vendor_lecture2notes():
    assert deploy.SUBMODULE_RELATIVE == "vendor/lecture2notes"
    assert deploy.SUBMODULE_PATH == ROOT / "vendor" / "lecture2notes"


def test_editable_install_uses_the_running_interpreter():
    assert deploy.PIP_COMMAND == [sys.executable, "-m", "pip"]


def test_overlay_source_holds_exactly_the_five_files():
    assert deploy.OVERLAY_SOURCE == ROOT / "skills-overlay" / "lecture2notes"
    for name in deploy.OVERLAY_FILES:
        assert (deploy.OVERLAY_SOURCE / name).is_file(), name
    assert len(deploy.OVERLAY_FILES) == 5


# --------------------------------------------------------------------------
# 2.1 deployment
# --------------------------------------------------------------------------
def test_deploy_runs_the_steps_in_order(harness, capsys):
    code = harness.deploy()
    out = capsys.readouterr().out
    assert code == 0, out

    calls = harness.calls()
    assert [call["tool"] for call in calls] == ["pip", "l2n", "l2n"]
    assert calls[0]["args"] == ["install", "-e", str(harness.submodule)]
    assert calls[1]["args"] == ["install-skill", "--all"]
    assert calls[2]["args"] == ["profile", "show", "--json"]


def test_deploy_copies_the_five_overlay_files_byte_for_byte(harness, capsys):
    assert harness.deploy() == 0, capsys.readouterr().out
    deployed = harness.overlay_dir()
    assert sorted(p.name for p in deployed.iterdir()) == sorted(deploy.OVERLAY_FILES)
    for name in deploy.OVERLAY_FILES:
        assert (deployed / name).read_bytes() == (
            deploy.OVERLAY_SOURCE / name
        ).read_bytes(), name


def test_deploy_keeps_other_files_in_the_overlay_directory(harness, capsys):
    keep = harness.overlay_dir()
    keep.mkdir(parents=True)
    (keep / "notes-of-my-own.txt").write_text("mine", encoding="utf-8")
    assert harness.deploy() == 0, capsys.readouterr().out
    assert (keep / "notes-of-my-own.txt").read_text(encoding="utf-8") == "mine"


def test_deploy_prints_one_ascii_progress_line_per_step(harness, capsys):
    harness.deploy()
    out = capsys.readouterr().out
    for number in range(1, deploy.TOTAL_STEPS + 1):
        assert "[step %d/5]" % number in out
    assert "[ok]" in out


def test_deploy_reports_the_effective_settings_with_their_layers(harness, capsys):
    harness.deploy()
    out = capsys.readouterr().out
    assert "profile = radiology  (user)" in out
    assert "note.style = faithful  (user)" in out
    assert "pbf = true  (user)" in out


def test_deploy_output_stays_inside_cp950(harness, capsys):
    harness.deploy()
    for line in capsys.readouterr().out.splitlines():
        line.encode("cp950")


def test_uninitialised_submodule_exits_2_and_installs_nothing(
    harness, tmp_path, capsys
):
    empty = tmp_path / "empty-submodule"
    empty.mkdir()
    harness.monkeypatch.setattr(deploy, "SUBMODULE_PATH", empty)

    code = harness.deploy()
    out = capsys.readouterr().out
    assert code == 2
    assert "run: git submodule update --init vendor/lecture2notes" in out
    assert harness.calls() == []
    assert not harness.overlay_dir().exists()


def test_missing_submodule_directory_exits_2(harness, tmp_path, capsys):
    harness.monkeypatch.setattr(deploy, "SUBMODULE_PATH", tmp_path / "absent")
    assert harness.deploy() == 2
    assert "run: git submodule update --init vendor/lecture2notes" in (
        capsys.readouterr().out
    )


def test_failed_editable_install_stops_before_the_skill_step(harness, capsys):
    harness.monkeypatch.setenv("PIP_STUB_EXIT", "1")
    code = harness.deploy()
    out = capsys.readouterr().out
    assert code == 2
    assert "[error]" in out
    assert [call["tool"] for call in harness.calls()] == ["pip"]


def test_missing_overlay_source_file_is_named_and_exits_2(
    harness, tmp_path, capsys
):
    partial = tmp_path / "overlay-source"
    partial.mkdir()
    for name in deploy.OVERLAY_FILES[:-1]:
        (partial / name).write_bytes((deploy.OVERLAY_SOURCE / name).read_bytes())
    harness.monkeypatch.setattr(deploy, "OVERLAY_SOURCE", partial)

    code = harness.deploy()
    out = capsys.readouterr().out
    assert code == 2
    assert deploy.OVERLAY_FILES[-1] in out


# --------------------------------------------------------------------------
# 2.2 drift check
# --------------------------------------------------------------------------
def test_check_passes_right_after_a_deployment(harness, capsys):
    assert harness.deploy() == 0, capsys.readouterr().out
    capsys.readouterr()

    code = harness.check()
    out = capsys.readouterr().out
    assert code == 0, out
    assert "[ok]" in out
    assert harness.calls()[-1]["args"] == ["install-skill", "--check", "--all"]


def test_check_names_an_overlay_file_changed_by_one_byte(harness, capsys):
    assert harness.deploy() == 0, capsys.readouterr().out
    capsys.readouterr()

    edited = harness.overlay_dir() / "outputs.toml"
    raw = bytearray(edited.read_bytes())
    raw[0] = raw[0] ^ 0x20
    edited.write_bytes(bytes(raw))

    code = harness.check()
    out = capsys.readouterr().out
    assert code == 2
    assert "outputs.toml" in out
    assert "[drift]" in out


def test_check_names_a_missing_overlay_file(harness, capsys):
    assert harness.deploy() == 0, capsys.readouterr().out
    capsys.readouterr()
    (harness.overlay_dir() / "corrections.json").unlink()

    code = harness.check()
    out = capsys.readouterr().out
    assert code == 2
    assert "corrections.json" in out


def test_check_fails_when_the_skill_check_fails(harness, capsys):
    assert harness.deploy() == 0, capsys.readouterr().out
    capsys.readouterr()
    harness.monkeypatch.setenv("L2N_STUB_EXIT", "2")

    assert harness.check() == 2
    assert "[error]" in capsys.readouterr().out


def test_check_exits_3_when_l2n_is_not_on_path(harness, capsys):
    harness.hide_l2n()
    code = harness.check()
    out = capsys.readouterr().out
    assert code == 3
    assert "deploy_lecture2notes.py" in out


def test_check_writes_nothing(harness, capsys):
    assert harness.deploy() == 0, capsys.readouterr().out
    before = harness.snapshot()
    capsys.readouterr()

    assert harness.check() == 0
    assert harness.snapshot() == before


def test_check_writes_nothing_even_when_it_reports_drift(harness, capsys):
    assert harness.deploy() == 0, capsys.readouterr().out
    (harness.overlay_dir() / "privacy.toml").unlink()
    before = harness.snapshot()
    capsys.readouterr()

    assert harness.check() == 2
    assert harness.snapshot() == before


def test_check_creates_no_overlay_directory_when_nothing_is_deployed(
    harness, capsys
):
    code = harness.check()
    out = capsys.readouterr().out
    assert code == 2
    assert not harness.overlay_dir().exists()
    for name in deploy.OVERLAY_FILES:
        assert name in out


def test_check_output_stays_inside_cp950(harness, capsys):
    harness.deploy()
    capsys.readouterr()
    harness.check()
    for line in capsys.readouterr().out.splitlines():
        line.encode("cp950")
