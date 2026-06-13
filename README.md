# rmf-package — Auto-generate SSP / POAM / SAR for eMASS / Xacta

[![CI](https://github.com/cognis-digital/rmf-package/workflows/CI/badge.svg)](https://github.com/cognis-digital/rmf-package/actions)
[![Classification](https://img.shields.io/badge/classification-UNCLASSIFIED-green.svg)](./UPSTREAM.md)

> Turn finding JSON into a full RMF accreditation package: SSP + POAM + SAR + OSCAL.

## Usage — step by step

`rmf-package` turns a findings JSON (or a directory of them) into NIST RMF authorization artifacts: SSP, POA&M, SAR, and an OSCAL skeleton.

1. **Install:**

   ```bash
   pip install cognis-rmf-package      # or: pip install -e .
   rmf-package --version
   ```

2. **Run against your findings** — the positional `target` is a findings JSON file or a directory (defaults to `.`). Console output by default:

   ```bash
   rmf-package ./findings.json --format console
   ```

3. **Emit specific artifacts** with `--emit` (comma-separated: `ssp,poam,sar,oscal`), naming the system and an output directory:

   ```bash
   rmf-package ./findings.json --emit ssp,poam,oscal \
     --system "Acme Mission System" --out-dir ./rmf-out
   ```

4. **Read the result** — generated artifacts land in the output directory; inspect the OSCAL skeleton or JSON summary:

   ```bash
   ls ./rmf-out
   rmf-package ./findings.json --format json | jq .
   ```

5. **Use it in automation** — chain it after a scanner (e.g. `mcpscan`/`tfscan`) in CI to keep the authorization package current:

   ```bash
   rmf-package ./scan-findings.json --emit ssp,poam,sar,oscal \
     --system "Acme Mission System" --out-dir ./rmf-out --format json
   ```

## Upstream

Forks / wraps **(original)**. See [`UPSTREAM.md`](./UPSTREAM.md) for the
licensing posture, supported commits, and how to upgrade.

## What this adds for military / IC use

- SSP (System Security Plan) generator — markdown
- POAM (Plan of Action & Milestones) — eMASS CSV
- SAR (Security Assessment Report) — markdown
- OSCAL 1.1 SSP skeleton — JSON
- Aggregates findings across multiple scan results

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
    pip install cognis-rmf-package
    rmf-package . --format=oscal --out=assessment-results.json --fail-on=high
- name: Upload to eMASS/Xacta
  run: cognis-rmf-package import assessment-results.json
```

## Part of the Cognis Digital military / IC ecosystem

12 repos. All MIT/Apache-2.0/GPL-3 (per upstream). Cognis additions are
Apache-2.0 unless stated otherwise.

See [the master index](../../MASTER-INDEX.md).

## Interoperability

`{}` composes with the 300+ tool Cognis suite — JSON in/out and a shared
OpenAI-compatible `/v1` backbone. See **[INTEROP.md](INTEROP.md)** for the
suite map, composition patterns, and reference stacks.
