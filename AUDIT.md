# Audit — rmf-package

Generated 2026-06-13 UTC.

```json
{
  "repo": "rmf-package",
  "parse_errors": [],
  "tests_passed": 6,
  "tests_failed": 0,
  "tests_errored": 0,
  "has_tests": true,
  "pytest_tail": "......                                                                   [100%]\n6 passed in 0.23s",
  "package": "rmf_package",
  "cli_version": "rmf-package 0.1.0",
  "clean": true
}
```

## pytest
```
......                                                                   [100%]
6 passed in 0.23s
```

## CLI
```
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
