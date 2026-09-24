---
name: "audio_transcript_extractor_skill"
description: "Extracts metadata and transcript snippets from encrypted school counseling audio backups (.m4a)."
aliases:
  - audio_transcript_extractor_skill
  - data-round-01-aligned-mix-800-0388-audio-transcript-extractor-skill
---

# audio_transcript_extractor_skill

## Description
Extracts metadata and transcript snippets from encrypted school counseling audio backups (.m4a).

## Parameters
- `file_path`: string, the path to the .m4a file.

## Response
- A JSON object with `session_id`, `counselor`, `duration_min`, and `date`.
