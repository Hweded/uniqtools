# UniqTools

UniqTools is a product-layer ecosystem built on top of the stable
[`uniqdiff`](https://github.com/Hweded/uniqdiff) comparison engine.

`uniqdiff` owns exact comparison semantics. UniqTools packages turn engine facts
into workflows, row-level analysis, reports, checks, and integrations.

## Current Packages

- [`packages/uniqrowdiff`](packages/uniqrowdiff/README.md): row-level
  changed-field analysis for CSV rows matched by key.
- [`packages/uniqcheck`](packages/uniqcheck/README.md): CI-friendly CSV checks
  for required columns, duplicate keys, and added/removed rows.

## Examples

- [`examples/uniqtools_starter`](examples/uniqtools_starter/README.md): minimal
  adapter around the public `uniqdiff` API.
- [`examples/uniqrowdiff_prototype`](examples/uniqrowdiff_prototype/README.md):
  original row-level diff sketch kept as a product-layer example.

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
$env:PYTHONPATH = "..\\uniq_remote_check\\src;packages\\uniqrowdiff\\src;packages\\uniqcheck\\src"
python -m uniqrowdiff --help
python -m uniqcheck --help
python -m pytest
```

Bash:

```bash
PYTHONPATH=../uniq_remote_check/src:packages/uniqrowdiff/src:packages/uniqcheck/src python -m uniqrowdiff --help
PYTHONPATH=../uniq_remote_check/src:packages/uniqrowdiff/src:packages/uniqcheck/src python -m uniqcheck --help
PYTHONPATH=../uniq_remote_check/src:packages/uniqrowdiff/src:packages/uniqcheck/src python -m pytest
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
