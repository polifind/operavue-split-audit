# Surgical-video split audit

A small, local Python tool for checking whether clips assigned to train, validation, and test sets share a source case, recording, or known patient group. It helps researchers inspect a split manifest before evaluating a model.

Published by [Operavue](https://operavue.com/resources#split-audit), a commercial surgical-data company. The included example is entirely synthetic and contains no patient data. This educational toolkit does not represent clinical-data inventory or a validated clinical system.

## Run the example

Requires Python 3.8 or later. No third-party packages, account, or upload are required.

```sh
python3 audit-surgical-splits.py surgical-split-example.csv
```

The supplied example has four clips from three invented procedures. Its two views of the first procedure both belong to training. The report returns `no_conflicts_found` and exit code `0`. Site and device overlap between training and validation is reported descriptively.

Read the [usage guide](surgical-split-audit-guide.md) for the required CSV columns and how to interpret findings. To audit your own manifest locally:

```sh
python3 audit-surgical-splits.py your-manifest.csv > split-report.json
```

Use project-specific pseudonymous identifiers. The report echoes supplied identifiers; keep both the input and report under your project's access controls. Do not put patient data in a public issue or pull request.

## Try a deliberate overlap

Copy the example CSV, then change the `synthetic-clip-001-right` row's split from `train` to `test`. Running the checker on that copy reports the shared case and patient group and exits with code `1`.

Exit codes:

- `0`: no conflicts found in the supplied identifiers; inspect warnings too.
- `1`: findings need review.
- `2`: the input could not be audited.

## Scope and limitations

The script checks exact supplied identifiers. It does not inspect video, detect visually duplicated media, resolve cross-dataset identity mappings, or establish statistical independence. It does not certify privacy, licensing, clinical validity, or generalization. Site and device overlap are descriptive, because the appropriate holdout depends on the study design.

The [dataset-quality guide](https://operavue.com/insights/evaluating-surgical-dataset-quality) explains the surrounding evaluation questions and links to primary references. For established dataset overlaps, follow the relevant dataset maintainers' guidance, including [CAMMA's overlap analysis](https://github.com/CAMMA-public/camma_dataset_overlaps).

## Files and provenance

The three toolkit files are unchanged copies of Operavue's public version 1.0 downloads, retrieved October 23, 2026:

- [Python source](https://operavue.com/downloads/audit-surgical-splits.py)
- [Usage guide](https://operavue.com/downloads/surgical-split-audit-guide.md)
- [Synthetic CSV](https://operavue.com/downloads/surgical-split-example.csv)

See [SOURCE.md](SOURCE.md) for SHA-256 checksums. This package contains only those public assets and packaging documentation.

## License

The Python source carries the [MIT License](LICENSE), reproduced unchanged from its header. The guide and synthetic example retain their original permission notice in the guide: they may be used and adapted for a project, and attribution is appreciated. The toolkit is educational planning material provided without warranty.
