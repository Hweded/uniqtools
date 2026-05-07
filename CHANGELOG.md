# Changelog

## Unreleased

- Updated packages to target `uniqdiff>=1.1,<2.0` and prefer the public
  `uniqdiff.engine` facade.
- Added `uniqprofile` for lightweight CSV, TSV, and JSONL file profiling.
- Added `uniqtools-cli` with a unified `uniqtools` command dispatcher.
- Moved `uniqrowdiff` field-change detection onto the `uniqdiff 1.1` field-diff
  engine while keeping product-layer duplicate-key policy and output shaping in
  UniqTools.
- Added `uniqcheck schema` backed by the `uniqdiff 1.1` schema-diff engine.
- Added the initial UniqTools workspace.
- Added `uniqrowdiff` scaffold for CSV row-level changed-field analysis.
- Added `uniqcheck` scaffold for CSV checks and CI-friendly exit codes.
- Added architecture documentation for the `uniqdiff` engine boundary.

## 0.1.0

Initial workspace preview. Not yet a stable public release.
