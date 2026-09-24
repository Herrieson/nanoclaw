---
name: "audio_metadata_extractor_skill"
description: "Extracts technical metadata from audio files (.wav, .mp3) to verify integrity."
aliases:
  - audio_metadata_extractor_skill
  - data-round-01-aligned-mix-800-0392-audio-metadata-extractor-skill
---

# audio_metadata_extractor_skill

Extracts technical metadata from audio files (.wav, .mp3) to verify integrity.

**Parameters:**
- `file_path`: Path to the audio file.

**Returns:**
JSON string containing `duration_seconds`, `sample_rate`, and `bit_depth`.
