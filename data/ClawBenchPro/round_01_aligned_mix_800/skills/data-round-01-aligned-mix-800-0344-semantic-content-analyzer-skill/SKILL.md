---
name: "semantic_content_analyzer_skill"
description: "An LLM-powered tool to extract specific semantic information (like mission statements, core values, or requirements) from messy text files, transcripts, or meeting notes."
aliases:
  - semantic_content_analyzer_skill
  - data-round-01-aligned-mix-800-0344-semantic-content-analyzer-skill
---

# semantic_content_analyzer_skill

## Description
An LLM-powered tool to extract specific semantic information (like mission statements, core values, or requirements) from messy text files, transcripts, or meeting notes.

## Parameters
- `file_path`: (Required) Path to the text file.
- `target_info`: (Required) Description of what you want to extract (e.g., "Mission Statement").

## Usage
Use this when a file contains too much conversational noise to be parsed reliably by simple regex.
