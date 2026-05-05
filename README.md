# UniqTools

UniqTools is a product-layer ecosystem built on top of the stable
[`uniqdiff`](https://github.com/Hweded/uniqdiff) comparison engine.

`uniqdiff` owns exact comparison semantics. UniqTools packages turn engine facts
into workflows, row-level analysis, reports, checks, and integrations.

## Current Packages

- [`packages/uniqrowdiff`](packages/uniqrowdiff/README.md): row-level
  changed-field analysis for CSV rows matched by key.

## Architecture

```text
files / streams / connectors
        |
        v
uniqdiff stable comparison engine
        |
        v
CompareResult / CompareStats / file result schema
        |
        v
UniqTools packages
        |
        v
row diff / reports / checks / workflows
```

## Development

Use both source roots during local development:

PowerShell:

```powershell
$env:PYTHONPATH = "..\\uniq_remote_check\\src;packages\\uniqrowdiff\\src"
python -m uniqrowdiff --help
python -m pytest packages\\uniqrowdiff\\tests -q
```

Bash:

```bash
PYTHONPATH=../uniq_remote_check/src:packages/uniqrowdiff/src python -m uniqrowdiff --help
PYTHONPATH=../uniq_remote_check/src:packages/uniqrowdiff/src python -m pytest packages/uniqrowdiff/tests -q
```

## Boundary Rule

UniqTools packages should depend only on public `uniqdiff` APIs:

- root package exports;
- `CompareResult` and `CompareStats`;
- file result schema and lazy readers;
- documented connector protocol.

UniqTools packages should not import `uniqdiff.core`, `uniqdiff.storage`,
`uniqdiff.planner`, backend modules, or private helper modules.

## License

Apache-2.0.
