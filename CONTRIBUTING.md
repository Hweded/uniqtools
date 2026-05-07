# Contributing

Thanks for helping improve UniqTools.

UniqTools packages are product-layer tools built on top of `uniqdiff`. Keep the
engine boundary clear:

- use public `uniqdiff` imports only;
- prefer `uniqdiff.engine` for stable 1.1 engine primitives;
- do not import `uniqdiff.core`, `uniqdiff.storage`, `uniqdiff.planner`, or
  private helper modules;
- keep reports, checks, row-level analysis, and workflows outside `uniqdiff`.

## Local Checks

PowerShell:

```powershell
$env:PYTHONPATH = "..\uniq_remote_check\src;packages\uniqrowdiff\src;packages\uniqcheck\src"
python -m ruff check .
python -m mypy packages\uniqrowdiff\src packages\uniqcheck\src
python -m pytest
```

## Commit Style

Use short, descriptive commits:

```text
Add uniqcheck duplicate key checks
Improve uniqrowdiff CLI summary
Document UniqTools package boundary
```

## Compatibility

Packages should depend on `uniqdiff>=1.1,<2.0` unless there is a documented
reason to require a newer major version.
