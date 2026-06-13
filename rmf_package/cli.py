import argparse, sys
from pathlib import Path
from cognis_mil import to_console, to_json
from .core import scan, load_findings, build_ssp, build_poam, build_sar, build_oscal_ssp_skeleton
from . import __version__
def main():
    p = argparse.ArgumentParser(prog="rmf-package")
    p.add_argument("target", nargs="?", default=".", help="Findings JSON file or dir")
    p.add_argument("--emit", default="", help="Comma-separated: ssp,poam,sar,oscal")
    p.add_argument("--system", default="PLACEHOLDER SYSTEM", help="System name (used in artifacts)")
    p.add_argument("-o","--out-dir", default="./rmf-out", help="Output directory")
    p.add_argument("--format", choices=["console","json"], default="console")
    p.add_argument("-v","--version", action="version", version=f"rmf-package {__version__}")
    args = p.parse_args()
    if args.emit:
        out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
        # Gather all findings
        p_t = Path(args.target)
        files = list(p_t.glob("*.json")) if p_t.is_dir() else [p_t]
        findings = []
        for f in files:
            if f.is_file():
                try: findings.extend(load_findings(f))
                except: pass
        if not findings:
            print("No findings found", file=sys.stderr); sys.exit(1)
        emit = set(s.strip() for s in args.emit.split(","))
        if "ssp" in emit:
            (out_dir / "ssp.md").write_text(build_ssp(findings, args.system)); print(f"✓ {out_dir/'ssp.md'}")
        if "poam" in emit:
            (out_dir / "poam.csv").write_text(build_poam(findings)); print(f"✓ {out_dir/'poam.csv'}")
        if "sar" in emit:
            (out_dir / "sar.md").write_text(build_sar(findings, args.system)); print(f"✓ {out_dir/'sar.md'}")
        if "oscal" in emit:
            (out_dir / "oscal-ssp.json").write_text(build_oscal_ssp_skeleton(args.system, findings))
            print(f"✓ {out_dir/'oscal-ssp.json'}")
        return
    r = scan(args.target, system_name=args.system)
    print(to_json(r) if args.format == "json" else to_console(r))
if __name__ == "__main__": main()
