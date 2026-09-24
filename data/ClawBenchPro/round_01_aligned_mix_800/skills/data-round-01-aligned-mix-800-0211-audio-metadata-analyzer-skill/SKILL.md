---
name: "AudioMetadataAnalyzer Skill"
description: "Extracts technical metadata (BPM, Key, Energy Level) from audio files."
aliases:
  - audio_metadata_analyzer_skill
  - data-round-01-aligned-mix-800-0211-audio-metadata-analyzer-skill
---

# AudioMetadataAnalyzer Skill

Extracts technical metadata (BPM, Key, Energy Level) from audio files.

## Usage
`python skills/data_round_01_aligned_mix_800_0211/audio_metadata_analyzer_skill.py --file_path <path>`

## Output
Returns a JSON string:
- `bpm`: Integer
- `energy`: 0.0-1.0
- `detected_key`: String
