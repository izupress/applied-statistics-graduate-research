# Release Workflow

This repository coordinates the book's public companion materials with the stable GitHub release used by readers.

## Routine Coordination

1. Update chapter data, code, figures, and support outputs.
2. Run `make manifest` to refresh `chapter-manifest.csv` and `support/chapter_manifest_report.json`.
3. Run `make chapter21` to refresh reporting, open-science, and AI-use audit outputs.
4. Run `make audit` before tagging a public release.
5. Commit the coordinated outputs and push to `main`.

## Stable Book Release

Use a Git tag for the release printed in the book or encoded in the QR code. Avoid pointing the printed book to a moving branch when a stable release artifact is available.

Suggested tag format:

```text
book-vYYYY.MM
```

## Files That Anchor Reproducibility

- `chapter-manifest.csv`
- `support/chapter_manifest_report.json`
- `support/python_reproducibility_audit.json`
- `support/chapter21_reporting_summary.csv`
- `support/chapter21_open_science_summary.csv`
- `support/chapter21_ai_risk_summary.csv`

