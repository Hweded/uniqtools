# uniqcheck

`uniqcheck` is a CI-friendly data checking tool built on top of the stable
`uniqdiff` engine.

It focuses on lightweight checks that are useful in scripts and pipelines:

- required CSV columns;
- duplicate key detection;
- comparison checks for added and removed rows.
- schema drift checks through the `uniqdiff 1.1` schema engine;
- UTF-8 BOM tolerant CSV reading through the default `utf-8-sig` encoding.

It is not a full data quality rule engine. Larger rule systems and workflow
orchestration belong in future UniqTools packages.

## Local Development

PowerShell:

```powershell
$env:PYTHONPATH = "..\..\uniq_remote_check\src;src"
python -m uniqcheck --help
```

From the UniqTools repository root:

```powershell
$env:PYTHONPATH = "..\uniq_remote_check\src;packages\uniqcheck\src"
python -m uniqcheck file users.csv --key id --required-column email --fail-on-duplicates
python -m uniqcheck compare old.csv new.csv --key id --fail-on-added --fail-on-removed
python -m uniqcheck schema old.csv new.csv --fail-on-schema-change
```

## Commands

```bash
uniqcheck file users.csv --key id --required-column email --fail-on-duplicates
uniqcheck compare old.csv new.csv --key id --fail-on-added --fail-on-removed
uniqcheck schema old.csv new.csv --sample-size 10000 --fail-on-schema-change
uniqcheck file export.csv --key id --encoding utf-8-sig
```

Exit codes:

- `0`: checks passed;
- `1`: at least one selected check failed;
- `2`: invalid input or usage error.

## Boundary Rule

`uniqcheck` should use only public `uniqdiff` imports such as
`uniqdiff.engine.compare_files` and `uniqdiff.engine.compare_file_schema`. It
must not import `uniqdiff` backend internals.
