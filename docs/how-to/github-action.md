# Use DEDoc in CI (GitHub Action)

Data Engineer Doctor ships a reusable composite action so you can diagnose
failure logs in any workflow. Point it at a log, a directory, or a glob; it
prints an evidence-backed report to the job summary and can fail the job when a
failure is diagnosed.

## Quick start

```yaml
name: diagnose
on:
  workflow_run:
    workflows: ["nightly-etl"]
    types: [completed]

jobs:
  dedoc:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Diagnose the failure log
        uses: Adez017/Data-Engineer-Doctor@main
        with:
          path: logs/job.log
          format: markdown
          fail-on: diagnosed
```

The action installs `data-engineer-doctor` from PyPI, runs `dedoc diagnose`
on each matched input, writes the report to `$GITHUB_STEP_SUMMARY`, and fails
the job when `fail-on` matches.

!!! note "Pin a released tag"
    The examples use `@main` because the action ships ahead of its first tagged
    release. For reproducible CI, pin to a release tag once available (and set
    `version` to match the installed package).

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `path` | yes | — | A log file, a directory, or a glob pattern (e.g. `logs/*.log`). |
| `format` | no | `markdown` | `text`, `markdown`, or `json`. |
| `output` | no | step summary | File to append reports to. Defaults to `$GITHUB_STEP_SUMMARY`. |
| `fail-on` | no | `never` | `never`, `diagnosed`, or `error`. |
| `version` | no | latest | Pin a specific `data-engineer-doctor` version, e.g. `0.1.0`. |
| `install` | no | `true` | Set `false` to use an existing `dedoc` on `PATH` (no install). |
| `color` | no | `never` | `auto`, `always`, or `never` for text output. |
| `diagnoses-path` | no | bundled | Override the diagnoses directory. |

## Failing the job on a diagnosis

Set `fail-on: diagnosed` to turn a diagnosed failure into a failed check. Use
`fail-on: error` to fail only on unparseable input, or `never` (default) to
always succeed and just publish the report.

To keep the step non-blocking while still seeing the result, combine
`continue-on-error` with that input in a separate step:

```yaml
- name: Diagnose (non-blocking)
  continue-on-error: true
  uses: Adez017/Data-Engineer-Doctor@main
  with:
    path: logs/
    fail-on: diagnosed
```

## Save the report as an artifact

```yaml
- name: Diagnose to a file
  uses: Adez017/Data-Engineer-Doctor@main
  with:
    path: logs/*.log
    format: json
    output: dedoc-report.json
    fail-on: never

- uses: actions/upload-artifact@v4
  with:
    name: dedoc-report
    path: dedoc-report.json
```

## Requirements

- A Python 3.11+ runtime on the runner (`actions/setup-python` is recommended).
- No AI key: diagnosis is fully deterministic and offline unless you opt in.
- Because the action resolves `path` from the repository root, check out your
  code first.
