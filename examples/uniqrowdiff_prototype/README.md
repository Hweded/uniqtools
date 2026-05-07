# uniqrowdiff Prototype

This is a legacy product-layer prototype for the `uniqrowdiff` package.

It demonstrates how a UniqTools package can build row-level changed-field
analysis on top of the stable `uniqdiff` engine without importing engine
internals.

## What It Does

The prototype compares two CSV files by a key column and reports:

- rows present only in the first file;
- rows present only in the second file;
- common keys;
- duplicate-key counts from the engine;
- changed fields for keys that exist exactly once in both files.

In `uniqdiff 1.1`, field-level comparison is now an engine primitive. The real
`packages/uniqrowdiff` package uses that public engine API. This prototype is
kept only as an older integration sketch.

## Run

From the repository root:

PowerShell:

```powershell
$env:PYTHONPATH = "..\uniq_remote_check\src"
python examples\uniqrowdiff_prototype\rowdiff.py
```

Bash:

```bash
PYTHONPATH=../uniq_remote_check/src python examples/uniqrowdiff_prototype/rowdiff.py
```

The script writes demo CSV files under `.tmp/uniqrowdiff_prototype`, generates a
JSONL row-diff artifact, prints a summary, and then removes the temporary
workspace.

## Future Package Shape

A future standalone package could expose:

```bash
uniqrowdiff old.csv new.csv --key id --output changes.jsonl
uniqrowdiff old.csv new.csv --key id --ignore updated_at --format csv
```

And depend on:

```toml
dependencies = ["uniqdiff>=1.1,<2.0"]
```

The package should continue to use only public imports from `uniqdiff`.
