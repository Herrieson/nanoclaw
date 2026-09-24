---
name: "Blueprint OCR Tracker Skill"
description: "Parses internal engineering data blobs from manifests and queries the central database to check for the current project status."
aliases:
  - blueprint_ocr_tracker_skill
  - data-round-01-aligned-mix-800-0385-blueprint-ocr-tracker-skill
---

# Blueprint OCR Tracker Skill

## Description
Parses internal engineering data blobs from manifests and queries the central database to check for the current project status.

## Parameters
- `content_blob`: (Required) The "BLOB" string extracted from the manifest file (e.g., "DATA:SCAN_BP_PHASE_1_RAW").

## Usage
Use this to determine if a blueprint is "OVERDUE", "ON TIME", or "PENDING".
