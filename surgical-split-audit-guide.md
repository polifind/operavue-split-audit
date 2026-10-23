# Audit a surgical-video split manifest

Version 1.0, October 18, 2026. Original tool by Operavue.

This small Python script checks whether identifiers in a CSV appear across train, validation, and test sets. It runs on your computer using only the Python standard library. It does not upload the manifest, inspect video, or contact Operavue.

Download [the Python source](https://operavue.com/downloads/audit-surgical-splits.py) and [the synthetic example CSV](https://operavue.com/downloads/surgical-split-example.csv). Review the source, then run with Python 3.8 or later:

```sh
python3 audit-surgical-splits.py surgical-split-example.csv
```

To save the JSON report locally:

```sh
python3 audit-surgical-splits.py your-manifest.csv > split-report.json
```

Exit code 0 means no conflicts were found in the supplied identifiers; 1 means findings need review; 2 means the input could not be audited. It does not modify your manifest. Review the warnings as well as the status.

## Prepare the rows

Use one row per delivered clip or view, with a unique clip ID. Keep related views, excerpts, re-encodings, augmentations, and annotations traceable to their source procedure. Use project-specific pseudonymous IDs, not names, medical-record numbers, or raw patient identifiers. The report echoes these IDs and should stay under your project's access controls. Pseudonymizing an ID does not establish de-identification of the underlying dataset.

| Column | Required? | Meaning |
| --- | --- | --- |
| clip_id | Yes | Unique delivered item identifier; each stereo eye may have its own row. |
| case_id | Yes | Stable source procedure identifier shared by all views and derivatives of that operation. |
| source_video_id | Yes | Stable original recording identifier shared by all clips derived from that recording. |
| split | Yes | Exactly `train`, `validation`, or `test`. |
| patient_group_id | Optional | Project-specific group that links repeat operations from the same person when authorized and available. |
| site_id | Optional | Study-defined acquisition site identifier. |
| device_id | Optional | Study-defined device instance or model identifier; document which meaning you use. |

Every identity must be consistent across the complete manifest. Identifiers are case-sensitive. Leading and trailing whitespace is removed. Different source IDs are treated as different groups even if their media are duplicates. When combining releases, resolve cross-dataset overlap before assigning IDs; simply prefixing a dataset name can hide the same source operation under two identities.

Do not include direct patient identifiers as extra columns. Unknown columns are ignored. The script does not validate their contents or infer an identity mapping.

## Interpret the output

- `cross_split_group` identifies a case, source video, or known patient group present in more than one split. Investigate the experiment's independence requirements before evaluating the model.
- `duplicate_clip_id` identifies repeated item IDs. A left/right stereo pair needs distinct item IDs and the same case ID.
- `missing_value` and `invalid_split` identify required-data problems. Required values cannot be blank.
- `incomplete_grouping` means patient, site, or device information is missing for some or all rows. An absent patient mapping prevents a patient-disjointness conclusion.
- `groups.site_id` and `groups.device_id` describe overlap. They are not automatic errors. A case-held-out evaluation can use the same sites or devices. It cannot thereby claim evaluation on unseen sites or device families.

The synthetic example has four rows representing three procedures and three invented patient groups. Both views of case 001 are in training. Site A and device A appear in training and validation. The tool reports this coverage without treating it as case leakage.

Try a deliberate failure: in a copy of the example, change the right-eye row's split from `train` to `test`. The script reports `synthetic-case-001` and `synthetic-patient-001` in both splits and exits with code 1.

## What this check cannot establish

This is a manifest check, not a duplicate-video detector, statistical independence test, clinical validation, license review, or privacy certification. It cannot find incorrectly mapped identities, image duplicates, shared pretraining sources missing from the manifest, or information leaked through model selection and preprocessing. The script loads the CSV in memory and is intended for a clip-level manifest, not a frame-by-frame export of a large archive.

Freeze a documented evaluation protocol and record all source releases and transformations. Case holdout, patient holdout, site holdout, device holdout, and temporal holdout answer different questions. Do not turn a clean JSON result into a broader claim than the identifiers and study design support.

See the [dataset quality guide](https://operavue.com/insights/evaluating-surgical-dataset-quality) for primary references and the [public dataset comparison](https://operavue.com/resources/surgical-video-datasets) for documented source overlaps. Questions or corrections can be submitted through [Operavue's business inquiry form](https://operavue.com/contact) without patient data.

The Python source is MIT licensed. You may use and adapt this guide and synthetic example for your project. Attribution is appreciated. Provided as educational planning material without warranty.
