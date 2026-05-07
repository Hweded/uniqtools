# uniqprofile

`uniqprofile` is a lightweight file profiler for UniqTools workflows.

It answers preflight questions before diff, checks, reports, or CI jobs:

- how many rows or records are present;
- which columns or fields exist;
- how many empty values appear per column;
- whether a key has duplicates;
- how large the input file is.

It does not perform exact diff itself. When comparison is needed, use
`uniqdiff`, `uniqcheck`, or `uniqrowdiff`.

## Commands

```bash
uniqprofile file users.csv --format csv --key id
uniqprofile file events.jsonl --format jsonl --key event_id --sample-size 10000
uniqprofile file export.tsv --format tsv --key id
```

Output is JSON by default so it can be consumed by CI and scripts.

## Boundary Rule

`uniqprofile` is product-layer profiling. It may use public `uniqdiff.engine`
helpers where useful, but it must not import backend internals.
