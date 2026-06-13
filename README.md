# rmf-package — Auto-generate SSP / POAM / SAR for eMASS / Xacta

[![CI](https://github.com/cognis-digital/rmf-package/workflows/CI/badge.svg)](https://github.com/cognis-digital/rmf-package/actions)
[![Classification](https://img.shields.io/badge/classification-UNCLASSIFIED-green.svg)](./UPSTREAM.md)

> Turn finding JSON into a full RMF accreditation package: SSP + POAM + SAR + OSCAL.

<!-- cognis:layman:start -->
## What is this?

rmf-package reads security scan findings and automatically produces the paperwork required to get a government or military IT system authorized to operate. It generates the System Security Plan (SSP), Plan of Action and Milestones (POAM), and Security Assessment Report (SAR) — documents that normally take days to write by hand — in seconds. The output files are ready to import directly into eMASS or Xacta, the two systems the Department of Defense uses to manage cybersecurity authorizations. It is built for security engineers, system administrators, and compliance teams working on DoD or federal government systems who need to meet NIST 800-37 Risk Management Framework requirements.
<!-- cognis:layman:end -->

## Upstream

Forks / wraps **(original)**. See [`UPSTREAM.md`](./UPSTREAM.md) for the
licensing posture, supported commits, and how to upgrade.

## What this adds for military / IC use

- SSP (System Security Plan) generator — markdown
- POAM (Plan of Action & Milestones) — eMASS CSV
- SAR (Security Assessment Report) — markdown
- OSCAL 1.1 SSP skeleton — JSON
- Aggregates findings across multiple scan results

<!-- cognis:install:start -->
## Install

`rmf-package` is source-available (not published to PyPI) — every method below installs
straight from GitHub. Pick whichever you prefer; the one-line scripts auto-detect
the best tool available on your machine.

**One-liner (Linux / macOS):**
```sh
curl -fsSL https://raw.githubusercontent.com/cognis-digital/rmf-package/HEAD/install.sh | sh
```

**One-liner (Windows PowerShell):**
```powershell
irm https://raw.githubusercontent.com/cognis-digital/rmf-package/HEAD/install.ps1 | iex
```

**Or install manually — any one of:**
```sh
pipx install "git+https://github.com/cognis-digital/rmf-package.git"     # isolated (recommended)
uv tool install "git+https://github.com/cognis-digital/rmf-package.git"  # uv
pip install "git+https://github.com/cognis-digital/rmf-package.git"      # pip
```

**From source:**
```sh
git clone https://github.com/cognis-digital/rmf-package.git
cd rmf-package && pip install .
```

Then run:
```sh
rmf-package --help
```
<!-- cognis:install:end -->

## Install

```bash
# Shared library (only once for the whole ecosystem):
pip install -e ../../shared

# This tool:
pip install -e .
```

## Demo

```bash
rmf-package demos/findings.json --emit ssp,poam,sar,oscal --system 'My System' -o rmf-out/
```

Outputs are available in five formats — all respect an operator-supplied
classification banner (passed via `--classification`):

```bash
rmf-package <target> --format=console     # default
rmf-package <target> --format=json
rmf-package <target> --format=sarif       # for code-scanning pipelines
rmf-package <target> --format=markdown    # for PRs / briefings
rmf-package <target> --format=oscal       # OSCAL Assessment Results skeleton
```

## Classification banner

All output is wrapped with an operator-supplied classification banner.
**Default**: `UNCLASSIFIED//FOR PUBLIC RELEASE`.

> ⚠️ This tool **does not** generate or validate the *content* of higher
> classifications. Operators on cleared systems supply real markings at runtime.
> See [`../shared/cognis_mil/classmark.py`](../../shared/cognis_mil/classmark.py).

## Compliance crosswalks (built in)

Every finding can carry references to:
- **NIST 800-53 Rev 5** controls (e.g. `AC-2(1)`)
- **DISA STIG** rule IDs (e.g. `V-242414`)
- **MITRE ATT&CK** technique IDs (e.g. `T1078`)
- **CCI** (Control Correlation Identifier)

These are emitted in JSON, SARIF, and the OSCAL skeleton.

## CI / RMF integration

```yaml
- name: rmf-package scan
  run: |
    pip install "git+https://github.com/cognis-digital/rmf-package.git"
    rmf-package . --format=oscal --out=assessment-results.json --fail-on=high
- name: Upload to eMASS/Xacta
  run: cognis-rmf-package import assessment-results.json
```

## Part of the Cognis Digital military / IC ecosystem

12 repos. All MIT/Apache-2.0/GPL-3 (per upstream). Cognis additions are
Apache-2.0 unless stated otherwise.

See [the master index](../../MASTER-INDEX.md).

<a name="verification"></a>
## Verification

[![tests](https://img.shields.io/badge/tests-6%20passing-2ea44f.svg)](AUDIT.md)

Every push is verified end-to-end. Latest audit (2026-06-13):

```text
tests        : 6 passed, 0 failed, 0 errored
compile      : all modules parse
cli          : rmf-package 0.1.0
package      : rmf_package
```

<details><summary>CLI surface (<code>--help</code>)</summary>

```text
usage: rmf-package [-h] [--emit EMIT] [--system SYSTEM] [-o OUT_DIR]
                   [--format {console,json}] [-v]
                   [target]

positional arguments:
  target                Findings JSON file or dir

options:
  -h, --help            show this help message and exit
  --emit EMIT           Comma-separated: ssp,poam,sar,oscal
  --system SYSTEM       System name (used in artifacts)
  -o, --out-dir OUT_DIR
                        Output directory
  --format {console,json}
```
</details>

Full machine-readable results: [`AUDIT.md`](AUDIT.md) · regenerate with `python -m rmf_package --help` + `pytest -q`.

<div align="right"><a href="#top">↑ back to top</a></div>

