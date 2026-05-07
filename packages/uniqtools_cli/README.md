# uniqtools-cli

`uniqtools-cli` provides one local command for the UniqTools ecosystem:

```bash
uniqtools profile file users.csv --key id
uniqtools check compare old.csv new.csv --key id --fail-on-added
uniqtools rowdiff old.csv new.csv --key id --output changes.jsonl
```

It is intentionally thin. Product logic stays in the package that owns it:

- `uniqprofile` owns profiling;
- `uniqcheck` owns CI-friendly checks;
- `uniqrowdiff` owns row-level changed-field workflows.

The direct package CLIs remain available.
