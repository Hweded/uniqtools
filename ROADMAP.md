# Roadmap

## 0.1

- Keep `uniqrowdiff` as the first row-level diff tool.
- Add `uniqcheck` for CSV checks and CI-friendly exit codes.
- Add `uniqprofile` for lightweight file profiling.
- Add `uniqtools-cli` as a thin unified command dispatcher.
- Keep all tools dependent only on public `uniqdiff` APIs.
- Target `uniqdiff>=1.1,<2.0` and prefer `uniqdiff.engine` for new engine
  primitives.
- Add basic documentation and repository metadata.

## 0.2

- Add JSONL event artifact support to `uniqrowdiff` and `uniqcheck`.
- Add shared test fixtures for package-level examples.
- Add richer shared fixtures for cross-package CLI examples.
- Add more practical recipes.

## 0.3

- Start `uniqreport` as a report renderer for JSONL artifacts.
- Expand `uniqprofile` with richer column statistics and optional sketches.
- Define shared artifact schemas across tools.

## 1.0

- Stabilize package APIs and CLI contracts.
- Publish selected packages independently.
- Document compatibility with `uniqdiff>=1.1,<2.0`.
