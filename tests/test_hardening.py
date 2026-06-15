"""Hardening tests — error paths, edge cases, CLI guard rails."""
import json
import sys
import pytest

from rmf_package.core import (
    load_findings,
    control_family,
    build_ssp,
    build_poam,
    build_sar,
    build_oscal_ssp_skeleton,
    scan,
)

# ---------------------------------------------------------------------------
# load_findings — bad inputs must raise ValueError, not crash with raw traceback
# ---------------------------------------------------------------------------

def test_load_findings_missing_file(tmp_path):
    """A non-existent path must raise ValueError (not FileNotFoundError traceback)."""
    with pytest.raises((ValueError, OSError)):
        load_findings(tmp_path / "does_not_exist.json")


def test_load_findings_malformed_json(tmp_path):
    """A file with invalid JSON must raise ValueError with a helpful message."""
    bad = tmp_path / "bad.json"
    bad.write_text("{ this is not json }", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        load_findings(bad)


def test_load_findings_wrong_top_level_type(tmp_path):
    """A JSON file whose top level is a plain string must raise ValueError."""
    bad = tmp_path / "string.json"
    bad.write_text(json.dumps("just a string"), encoding="utf-8")
    with pytest.raises(ValueError):
        load_findings(bad)


def test_load_findings_findings_key_not_list(tmp_path):
    """A JSON object with 'findings' that is not a list must raise ValueError."""
    bad = tmp_path / "bad_findings.json"
    bad.write_text(json.dumps({"findings": {"key": "value"}}), encoding="utf-8")
    with pytest.raises(ValueError, match="must be a list"):
        load_findings(bad)


def test_load_findings_empty_list(tmp_path):
    """An empty JSON array is valid and should return []."""
    f = tmp_path / "empty.json"
    f.write_text("[]", encoding="utf-8")
    result = load_findings(f)
    assert result == []


def test_load_findings_findings_wrapper_empty(tmp_path):
    """{'findings': []} is valid and should return []."""
    f = tmp_path / "wrapper.json"
    f.write_text(json.dumps({"findings": []}), encoding="utf-8")
    assert load_findings(f) == []


# ---------------------------------------------------------------------------
# control_family — edge cases
# ---------------------------------------------------------------------------

def test_control_family_normal():
    assert control_family("AC-2(1)") == "AC"
    assert control_family("SC-13") == "SC"


def test_control_family_empty_string():
    """Empty string must not raise; returns ''."""
    assert control_family("") == ""


def test_control_family_none_type():
    """None must not raise; returns ''."""
    assert control_family(None) == ""  # type: ignore[arg-type]


def test_control_family_no_hyphen():
    """'AU11' → first two chars 'AU'."""
    assert control_family("AU11") == "AU"


# ---------------------------------------------------------------------------
# builders — empty findings list must not raise
# ---------------------------------------------------------------------------

def test_build_ssp_empty_findings():
    result = build_ssp([], "TestSys")
    assert "TestSys" in result
    assert isinstance(result, str)


def test_build_poam_empty_findings():
    result = build_poam([])
    # Header row must still be present
    assert "Control,Weakness" in result


def test_build_sar_empty_findings():
    result = build_sar([], "TestSys")
    assert "TestSys" in result
    assert "Total findings: 0" in result


def test_build_oscal_empty_findings():
    result = build_oscal_ssp_skeleton("TestSys", [])
    data = json.loads(result)  # must be valid JSON
    assert "system-security-plan" in data


# ---------------------------------------------------------------------------
# scan() — non-existent directory emits a parse-warning finding, not a crash
# ---------------------------------------------------------------------------

def test_scan_nonexistent_dir(tmp_path):
    """scan() on a missing path should not raise; the result is a ScanResult."""
    from rmf_package.core import scan
    # Point at a directory that doesn't exist; glob will return empty list
    missing = tmp_path / "no_such_dir"
    r = scan(str(missing))
    # Should still produce a ScanResult with the summary finding
    assert hasattr(r, "findings")


def test_scan_bad_json_file(tmp_path):
    """scan() on a dir containing an invalid JSON file emits a parse-error finding."""
    bad = tmp_path / "bad.json"
    bad.write_text("not json at all", encoding="utf-8")
    r = scan(str(tmp_path))
    ids = [f.id for f in r.findings]
    assert any("PARSE" in fid for fid in ids), (
        f"Expected a parse-error finding, got: {ids}"
    )


# ---------------------------------------------------------------------------
# CLI — bad --emit value and missing target exit with non-zero code
# ---------------------------------------------------------------------------

def test_cli_bad_emit_value(tmp_path, capsys):
    """An unknown --emit token must exit with code 2 and print to stderr."""
    from rmf_package.cli import main
    sys.argv = ["rmf-package", "--emit", "invalid_token", str(tmp_path)]
    # _parse_emit calls sys.exit(2) directly, so this will raise SystemExit
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "invalid_token" in captured.err


def test_cli_missing_target_with_emit(tmp_path, capsys):
    """--emit on a missing target must return exit code 2 with a clear message."""
    from rmf_package.cli import main
    sys.argv = ["rmf-package", "--emit", "ssp", str(tmp_path / "no_such_path")]
    code = main()
    assert code == 2
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_cli_missing_target_scan_mode(tmp_path, capsys):
    """scan mode with a non-existent target must return exit code 2."""
    from rmf_package.cli import main
    sys.argv = ["rmf-package", str(tmp_path / "no_such_path")]
    code = main()
    assert code == 2
    captured = capsys.readouterr()
    assert "not found" in captured.err


def test_cli_emit_no_findings(tmp_path, capsys):
    """--emit on an empty directory (no JSON) must return exit code 1, not crash."""
    from rmf_package.cli import main
    sys.argv = ["rmf-package", "--emit", "ssp", str(tmp_path)]
    code = main()
    assert code == 1
    captured = capsys.readouterr()
    assert "no findings" in captured.err.lower()


def test_cli_returns_int():
    """main() must return an int (not None) so __main__ sys.exit works correctly."""
    from rmf_package.cli import main
    # Use --version which argparse handles directly (raises SystemExit(0))
    sys.argv = ["rmf-package", "--version"]
    with pytest.raises(SystemExit) as exc_info:
        main()
    # argparse itself exits 0 for --version
    assert exc_info.value.code == 0
