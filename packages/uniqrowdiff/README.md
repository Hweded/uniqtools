# uniqrowdiff

`uniqrowdiff` is the first UniqTools package prototype built on top of the
stable `uniqdiff` engine.

It answers a product-layer question that does not belong in `uniqdiff` itself:

> For rows with the same key, which fields changed?

`uniqdiff 1.1` remains responsible for exact presence comparison, duplicate
counts, and the engine-level field-diff primitive. `uniqrowdiff` consumes those
facts and adds product policies such as duplicate-key skipping, CI exit codes,
and tool-specific JSONL output.

## Current Scope

This scaffold currently supports:

- CSV input;
- key-based matching;
- engine-backed field diff through `uniqdiff.engine`;
- ignored fields;
- selected-column comparison;
- sorted-input mode for already key-sorted CSV files;
- output limits for changed rows and bytes;
- UTF-8 BOM tolerant CSV reading through the default `utf-8-sig` encoding;
- JSONL output for changed rows;
- summary JSON for CLI/CI;
- optional non-zero exit code when changes, added rows, or removed rows are
  found.

It intentionally does not include reports, dashboards, workflow orchestration,
or enterprise connector management.

## Local Development

From the repository root, use both source roots on `PYTHONPATH`.

PowerShell:

```powershell
$env:PYTHONPATH = "..\uniq_remote_check\src;packages\uniqrowdiff\src"
python -m uniqrowdiff --help
python -m uniqrowdiff old.csv new.csv --key id --output changes.jsonl
```

Bash:

```bash
PYTHONPATH=../uniq_remote_check/src:packages/uniqrowdiff/src python -m uniqrowdiff --help
PYTHONPATH=../uniq_remote_check/src:packages/uniqrowdiff/src python -m uniqrowdiff old.csv new.csv --key id --output changes.jsonl
```

## CLI Examples

```bash
uniqrowdiff old.csv new.csv --key id --ignore updated_at --output changes.jsonl
uniqrowdiff old.csv new.csv --key id --column status --column score
uniqrowdiff old.csv new.csv --key id --sorted-input --max-rows 1000
uniqrowdiff old.csv new.csv --key id --fail-on-changes
uniqrowdiff old.csv new.csv --key id --fail-on-added --fail-on-removed
```

Exit codes:

- `0`: command completed and no selected failure condition was triggered;
- `1`: selected failure condition was triggered;
- `2`: invalid input or usage error.

## Architecture Rule

This package should depend only on public `uniqdiff` imports:

```python
from uniqdiff.engine import CompareResult, compare_file_fields, compare_files
```

It should not import `uniqdiff.core`, `uniqdiff.storage`, `uniqdiff.planner`, or
private helper modules.
