---
name: "Bird Call Analyzer Skill"
description: "This skill allows you to identify bird species based on technical audio log metadata (frequency, pattern, and log ID)."
aliases:
  - bird_call_analyzer_skill
  - data-round-01-aligned-mix-800-0380-bird-call-analyzer-skill
---

# Bird Call Analyzer Skill

This skill allows you to identify bird species based on technical audio log metadata (frequency, pattern, and log ID).

## Usage
Call the `bird_call_analyzer_skill.py` script with the content of a `.wav.log` file.

## Input Format
A string containing the log entry.

## Output
Returns a JSON string with the identified `species` and `confidence_score`.
