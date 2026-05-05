# Security Policy

UniqTools processes local files and user-provided paths. Treat inputs as
untrusted data.

## Supported Versions

The project is currently pre-1.0 as an ecosystem workspace. Security fixes are
applied to the latest `main` branch.

## Reporting

Report security concerns privately by email:

```text
dredpirite@gmail.com
```

Please include:

- affected package;
- input format and command used;
- expected behavior;
- observed behavior;
- minimal reproduction if possible.

## Scope

Security-sensitive areas include:

- path handling;
- temporary files;
- parsing malformed CSV/JSONL-like inputs;
- future report generation;
- future connector implementations.
