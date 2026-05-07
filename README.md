# UniqTools

UniqTools is a product-layer ecosystem built on top of the stable
[`uniqdiff`](https://github.com/Hweded/uniqdiff) comparison engine.

`uniqdiff` owns exact comparison semantics. UniqTools packages turn engine facts
into workflows, row-level analysis, reports, checks, and integrations.

Current UniqTools development targets `uniqdiff>=1.1,<2.0`. Tools should prefer
the public `uniqdiff.engine` facade for engine primitives introduced after 1.0,
including field diff, schema diff, sorted streaming diff, and JSONL event readers.

## Current Packages

- [`packages/uniqrowdiff`](packages/uniqrowdiff/README.md): row-level
  changed-field analysis for CSV rows matched by key.
- [`packages/uniqcheck`](packages/uniqcheck/README.md): CI-friendly CSV checks
  for required columns, duplicate keys, and added/removed rows.
- [`packages/uniqprofile`](packages/uniqprofile/README.md): lightweight CSV, TSV,
  and JSONL profiling for workflow preflight.
- [`packages/uniqtools_cli`](packages/uniqtools_cli/README.md): unified `uniqtools`
  command that delegates to package CLIs.

## Unified CLI

```bash
uniqtools profile file users.csv --key id
uniqtools check schema old.csv new.csv --fail-on-schema-change
uniqtools rowdiff old.csv new.csv --key id --column status --output changes.jsonl
```

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
field diff / schema diff / JSONL event stream
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
$env:PYTHONPATH = "..\\uniq_remote_check\\src;packages\\uniqrowdiff\\src;packages\\uniqcheck\\src;packages\\uniqprofile\\src;packages\\uniqtools_cli\\src"
python -m uniqrowdiff --help
python -m uniqcheck --help
python -m uniqprofile --help
python -m uniqtools_cli --help
python -m pytest
```

Bash:

```bash
PYTHONPATH=../uniq_remote_check/src:packages/uniqrowdiff/src:packages/uniqcheck/src:packages/uniqprofile/src:packages/uniqtools_cli/src python -m uniqrowdiff --help
PYTHONPATH=../uniq_remote_check/src:packages/uniqrowdiff/src:packages/uniqcheck/src:packages/uniqprofile/src:packages/uniqtools_cli/src python -m uniqcheck --help
PYTHONPATH=../uniq_remote_check/src:packages/uniqrowdiff/src:packages/uniqcheck/src:packages/uniqprofile/src:packages/uniqtools_cli/src python -m uniqprofile --help
PYTHONPATH=../uniq_remote_check/src:packages/uniqrowdiff/src:packages/uniqcheck/src:packages/uniqprofile/src:packages/uniqtools_cli/src python -m pytest
```

## Boundary Rule

UniqTools packages should depend only on public `uniqdiff` APIs:

- root package exports;
- `uniqdiff.engine` facade exports;
- `CompareResult` and `CompareStats`;
- file result schema and lazy readers;
- field diff and schema diff result objects;
- `uniqdiff.jsonl` event stream readers;
- documented connector protocol.

UniqTools packages should not import `uniqdiff.core`, `uniqdiff.storage`,
`uniqdiff.planner`, backend modules, or private helper modules.

## License

Apache-2.0.
