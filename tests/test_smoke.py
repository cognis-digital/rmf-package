from pathlib import Path
from rmf_package.core import build_ssp, build_poam, build_sar, build_oscal_ssp_skeleton, scan, load_findings
D = Path(__file__).parent.parent / "demos"
def test_load():
    findings = load_findings(D / "findings.json")
    assert len(findings) == 4
def test_ssp_emits_families():
    findings = load_findings(D / "findings.json")
    ssp = build_ssp(findings, "Test")
    assert "AC" in ssp and "SC" in ssp
    assert "Test" in ssp
def test_poam_csv():
    findings = load_findings(D / "findings.json")
    poam = build_poam(findings)
    assert "Control,Weakness" in poam
    assert "SC-13" in poam
def test_sar():
    findings = load_findings(D / "findings.json")
    sar = build_sar(findings, "Test")
    assert "Security Assessment Report" in sar
    assert "very_high" in sar
def test_oscal():
    findings = load_findings(D / "findings.json")
    oscal = build_oscal_ssp_skeleton("Test", findings)
    assert "system-security-plan" in oscal
    assert "1.1.0" in oscal
def test_scan_summary():
    r = scan(str(D))
    assert any(f.id == "RP-SUMMARY" for f in r.findings)
