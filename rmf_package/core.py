"""rmf-package — generate accreditation artifacts from scan findings.

Outputs:
  - SSP (System Security Plan) — Markdown + OSCAL component-definition
  - POAM (Plan of Action and Milestones) — eMASS-compatible CSV
  - SAR (Security Assessment Report) — Markdown
  - OSCAL System Security Plan (skeleton)

Public references:
  - NIST 800-18 (SSP)
  - NIST 800-37 (RMF)
  - NIST 800-53 Rev 5 (controls)
  - DoDI 8510.01 (DoD RMF)
"""
from __future__ import annotations
import csv, io, json
from pathlib import Path
from cognis_mil import ScanResult, Finding, Severity

# 800-53 family list (public — full text is at csrc.nist.gov)
FAMILIES = {
    "AC":"Access Control", "AT":"Awareness & Training", "AU":"Audit & Accountability",
    "CA":"Assessment, Authorization & Monitoring", "CM":"Configuration Management",
    "CP":"Contingency Planning", "IA":"Identification & Authentication",
    "IR":"Incident Response", "MA":"Maintenance", "MP":"Media Protection",
    "PE":"Physical & Environmental", "PL":"Planning", "PM":"Program Management",
    "PS":"Personnel Security", "PT":"PII Processing & Transparency", "RA":"Risk Assessment",
    "SA":"System & Services Acquisition", "SC":"System & Communications Protection",
    "SI":"System & Information Integrity", "SR":"Supply Chain Risk Management",
}

def control_family(ctrl_id: str) -> str:
    """Given 'AC-2(1)' return 'AC'. Returns '' for blank/invalid input."""
    if not ctrl_id or not isinstance(ctrl_id, str):
        return ""
    return ctrl_id.split("-")[0] if "-" in ctrl_id else ctrl_id[:2]

def load_findings(path: Path) -> list[dict]:
    """Accept JSON list of finding dicts (as produced by cognis_mil ScanResult).

    Raises:
        ValueError: if the file cannot be read or does not contain a valid
                    JSON object/list structure.
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except PermissionError as exc:
        raise ValueError(f"Permission denied reading {path}") from exc
    except OSError as exc:
        raise ValueError(f"Cannot read {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if isinstance(data, dict) and "findings" in data:
        items = data["findings"]
        if not isinstance(items, list):
            raise ValueError(
                f"'findings' key in {path} must be a list, got {type(items).__name__}"
            )
        return items
    if isinstance(data, list):
        return data
    raise ValueError(
        f"{path} must contain a JSON list or a JSON object with a 'findings' list; "
        f"got {type(data).__name__}"
    )

def build_ssp(findings: list[dict], system_name: str = "PLACEHOLDER SYSTEM") -> str:
    """Build a basic SSP in Markdown."""
    controls_addressed = {f.get("nist_800_53","") for f in findings if f.get("nist_800_53")}
    by_family = {}
    for c in sorted(controls_addressed):
        if c: by_family.setdefault(control_family(c), []).append(c)
    md = [
        f"# System Security Plan — {system_name}",
        "",
        "> **UNCLASSIFIED//PLACEHOLDER** — operator on cleared system supplies real markings.",
        "",
        "## 1. System Identification",
        f"- **System Name:** {system_name}",
        "- **System Owner:** PLACEHOLDER",
        "- **ATO Status:** PLACEHOLDER",
        "- **Categorization (FIPS 199):** PLACEHOLDER (e.g. MODERATE-MODERATE-MODERATE)",
        "",
        "## 2. System Environment",
        "- **Description:** PLACEHOLDER",
        "- **Boundary:** PLACEHOLDER (cf. architecture diagram)",
        "",
        "## 3. Security Controls Addressed",
        "",
    ]
    for fam, ctrls in sorted(by_family.items()):
        md.append(f"### {fam} — {FAMILIES.get(fam, '(unknown family)')}")
        for c in ctrls: md.append(f"- `{c}` (see POAM for findings)")
        md.append("")
    md.append("## 4. Identified Weaknesses")
    for f in findings[:50]:
        md.append(f"- **{f.get('id','?')}** ({f.get('severity','?')}): {f.get('title','?')} → {f.get('nist_800_53','?')}")
    md.append("")
    md.append("> See `poam.csv` and `oscal-ssp.json` for machine-readable artifacts.")
    return "\n".join(md)

def build_poam(findings: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Control","Weakness","Severity","SCD","Estimated Completion","Status","POC","Resources Required","Source"])
    for f in findings:
        w.writerow([
            f.get("nist_800_53","") or "(none)",
            f.get("title",""),
            f.get("severity",""),
            "TBD", "TBD", "Open", "TBD", "TBD",
            f"STIG {f.get('disa_stig','')} / CCI {f.get('cci','')} / ATT&CK {f.get('mitre_attack','')}".strip(),
        ])
    return buf.getvalue()

def build_sar(findings: list[dict], system_name: str = "PLACEHOLDER SYSTEM") -> str:
    from collections import Counter
    sev_count = Counter(f.get("severity","") for f in findings)
    md = [
        f"# Security Assessment Report — {system_name}",
        "",
        "## Executive Summary",
        f"- Total findings: {len(findings)}",
    ]
    for sev in ("very_high","high","moderate","low","very_low"):
        md.append(f"- {sev}: {sev_count.get(sev, 0)}")
    md += ["", "## Findings Detail", "", "| ID | Severity | Title | Control |", "|----|----|----|----|"]
    for f in findings:
        md.append(f"| `{f.get('id','?')}` | {f.get('severity','?')} | {f.get('title','?')} | {f.get('nist_800_53','?')} |")
    return "\n".join(md)

def build_oscal_ssp_skeleton(system_name: str, findings: list[dict]) -> str:
    return json.dumps({
        "system-security-plan":{
            "uuid":"00000000-0000-0000-0000-000000000000",
            "metadata":{"title": f"SSP — {system_name}",
                        "version":"0.1.0","oscal-version":"1.1.0",
                        "remarks":"PLACEHOLDER — operator supplies UUIDs, parties, profile"},
            "system-characteristics":{"system-name": system_name, "security-sensitivity-level":"PLACEHOLDER"},
            "control-implementation":{
                "implemented-requirements":[
                    {"uuid": f"req-{i}",
                     "control-id": f.get("nist_800_53","").lower().replace("(","_").replace(")",""),
                     "remarks": f.get("title","")}
                    for i, f in enumerate(findings) if f.get("nist_800_53")
                ]
            }
        }
    }, indent=2)

def scan(target=".", system_name="PLACEHOLDER SYSTEM", **opts):
    """Given a directory of finding JSON files, generate full RMF package."""
    r = ScanResult(tool_name="rmf-package", tool_version="0.1.0")
    p = Path(target)
    files = list(p.glob("*.json")) if p.is_dir() else [p]
    all_findings = []
    for f in files:
        if f.is_file():
            try:
                all_findings.extend(load_findings(f))
            except (ValueError, OSError) as e:
                r.add(Finding(
                    f"RP-PARSE-{f.stem}", Severity.LOW,
                    f"Couldn't parse {f.name}: {e}",
                    location=str(f),
                ))
    r.items_scanned = len(all_findings)
    from collections import Counter
    sev_count = Counter(f.get("severity","") for f in all_findings)
    r.meta = {"findings_loaded": len(all_findings), "by_severity": dict(sev_count)}
    # Emit summary finding only — generation happens via CLI flags
    sev = Severity.HIGH if sev_count.get("very_high",0) + sev_count.get("high",0) > 0 else Severity.LOW
    r.add(Finding("RP-SUMMARY", sev,
                  f"{len(all_findings)} findings ready for RMF package",
                  location=str(p),
                  remediation="rmf-package <dir> --emit ssp,poam,sar,oscal --system 'Name'"))
    r.finalize(); return r
