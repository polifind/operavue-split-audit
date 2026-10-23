#!/usr/bin/env python3
"""Operavue split audit v1.0. Local CSV checks, Python 3.8+, no dependencies.

Read the companion guide before use. No network requests or media inspection.
MIT License
Copyright (c) 2026 Operavue

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import argparse
import csv
import json
import sys
from collections import defaultdict

REQUIRED = ("clip_id", "case_id", "source_video_id", "split")
OPTIONAL = ("patient_group_id", "site_id", "device_id")
SPLITS = {"train", "validation", "test"}


def audit(handle):
    reader = csv.DictReader(handle, strict=True)
    fields = reader.fieldnames or []
    if len(fields) != len(set(fields)):
        raise ValueError("Duplicate column names are not supported.")
    missing = [key for key in REQUIRED if key not in fields]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    rows = []
    for row in reader:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("A row has a different number of fields than its header.")
        rows.append({key: value.strip() for key, value in row.items()})
    if not rows:
        raise ValueError("The CSV contains no data rows.")

    errors = []
    for number, row in enumerate(rows, 2):
        for key in REQUIRED:
            if not row[key]:
                errors.append({"type": "missing_value", "row": number, "field": key})
        if row["split"] not in SPLITS:
            errors.append({"type": "invalid_split", "row": number, "value": row["split"]})

    clip_rows = defaultdict(list)
    for number, row in enumerate(rows, 2):
        if row["clip_id"]:
            clip_rows[row["clip_id"]].append(number)
    for clip, numbers in sorted(clip_rows.items()):
        if len(numbers) > 1:
            errors.append({"type": "duplicate_clip_id", "clip_id": clip, "rows": numbers})

    groups = {}
    for field in ("case_id", "source_video_id") + OPTIONAL:
        memberships = defaultdict(set)
        missing_count = 0
        for row in rows:
            value = row.get(field, "")
            if not value:
                missing_count += 1
            elif row["split"] in SPLITS:
                memberships[value].add(row["split"])
        shared = [{"id": key, "splits": sorted(value)}
                  for key, value in sorted(memberships.items()) if len(value) > 1]
        groups[field] = {"unique_ids": len(memberships), "missing_rows": missing_count,
                         "shared_across_splits": shared}
        if field in ("case_id", "source_video_id", "patient_group_id"):
            for group in shared:
                errors.append({"type": "cross_split_group", "field": field, **group})

    warnings = []
    for field in OPTIONAL:
        if groups[field]["missing_rows"]:
            warnings.append({"type": "incomplete_grouping", "field": field,
                             "missing_rows": groups[field]["missing_rows"]})
    present = sorted({row["split"] for row in rows if row["split"] in SPLITS})
    if len(present) < 2:
        warnings.append({"type": "fewer_than_two_splits", "splits": present})
    return {"tool": "Operavue split audit", "version": "1.0", "row_count": len(rows),
            "splits_present": present, "status": "issues_found" if errors else "no_conflicts_found",
            "errors": errors, "warnings": warnings, "groups": groups,
            "scope": "Exact supplied identifiers only. No-conflicts-found is not proof of independence, de-identification, clinical validity, or generalization. Site and device overlap are descriptive, not errors."}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", help="Local CSV with clip_id, case_id, source_video_id, split")
    args = parser.parse_args()
    try:
        with open(args.manifest, newline="", encoding="utf-8-sig") as handle:
            result = audit(handle)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(json.dumps({"status": "invalid_input", "error": str(error)}, ensure_ascii=True))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
