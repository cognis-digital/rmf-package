import argparse
import sys
from pathlib import Path

from cognis_mil import to_console, to_json
from .core import (
    scan, load_findings, build_ssp, build_poam, build_sar, build_oscal_ssp_skeleton,
)
from . import __version__

VALID_EMITTERS = {"ssp", "poam", "sar", "oscal"}


def _parse_emit(raw: str) -> set[str]:
    """Parse and validate the --emit comma list; exits with code 2 on bad values."""
    parts = {s.strip().lower() for s in raw.split(",") if s.strip()}
    unknown = parts - VALID_EMITTERS
    if unknown:
        print(
            f"rmf-package: unknown --emit value(s): {', '.join(sorted(unknown))}. "
            f"Valid choices: {', '.join(sorted(VALID_EMITTERS))}",
            file=sys.stderr,
        )
        sys.exit(2)
    return parts


def main() -> int:  # always returns an int exit code
    p = argparse.ArgumentParser(prog="rmf-package")
    p.add_argument("target", nargs="?", default=".", help="Findings JSON file or dir")
    p.add_argument("--emit", default="", help="Comma-separated: ssp,poam,sar,oscal")
    p.add_argument(
        "--system", default="PLACEHOLDER SYSTEM", help="System name (used in artifacts)"
    )
    p.add_argument("-o", "--out-dir", default="./rmf-out", help="Output directory")
    p.add_argument("--format", choices=["console", "json"], default="console")
    p.add_argument(
        "-v", "--version", action="version", version=f"rmf-package {__version__}"
    )
    args = p.parse_args()

    try:
        return _run(args)
    except KeyboardInterrupt:
        print("\nrmf-package: interrupted", file=sys.stderr)
        return 130
    except Exception as exc:  # unexpected — show clean message, not traceback
        print(f"rmf-package: unexpected error: {exc}", file=sys.stderr)
        return 1


def _run(args) -> int:
    p_t = Path(args.target)

    if args.emit:
        emit = _parse_emit(args.emit)

        # Validate target exists
        if not p_t.exists():
            print(f"rmf-package: target not found: {args.target}", file=sys.stderr)
            return 2

        # Prepare output directory
        out_dir = Path(args.out_dir)
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            print(
                f"rmf-package: cannot create output directory {out_dir}: {exc}",
                file=sys.stderr,
            )
            return 1

        # Gather all findings
        files = list(p_t.glob("*.json")) if p_t.is_dir() else [p_t]
        findings: list[dict] = []
        parse_errors: list[str] = []
        for f in files:
            if f.is_file():
                try:
                    findings.extend(load_findings(f))
                except ValueError as exc:
                    parse_errors.append(str(exc))

        for err in parse_errors:
            print(f"rmf-package: parse warning: {err}", file=sys.stderr)

        if not findings:
            print("rmf-package: no findings found — nothing to emit", file=sys.stderr)
            return 1

        def _write(dest: Path, content: str) -> bool:
            try:
                dest.write_text(content, encoding="utf-8")
                print(f"  {dest}")
                return True
            except OSError as exc:
                print(f"rmf-package: cannot write {dest}: {exc}", file=sys.stderr)
                return False

        ok = True
        if "ssp" in emit:
            ok &= _write(out_dir / "ssp.md", build_ssp(findings, args.system))
        if "poam" in emit:
            ok &= _write(out_dir / "poam.csv", build_poam(findings))
        if "sar" in emit:
            ok &= _write(out_dir / "sar.md", build_sar(findings, args.system))
        if "oscal" in emit:
            ok &= _write(
                out_dir / "oscal-ssp.json",
                build_oscal_ssp_skeleton(args.system, findings),
            )

        return 0 if ok else 1

    # Scan / summary mode
    if not p_t.exists():
        print(f"rmf-package: target not found: {args.target}", file=sys.stderr)
        return 2

    r = scan(args.target, system_name=args.system)
    print(to_json(r) if args.format == "json" else to_console(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
