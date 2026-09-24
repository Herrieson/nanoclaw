---
name: "nexus_content_moderation"
description: "The state-of-art text content moderation gateway connected to Nexus infrastructure. It evaluates AI or human generated text for toxicity, violence, hate speech, and destructive prompts."
aliases:
  - nexus_content_moderation
  - data-persona-aligned-skills-50-0048-nexus-content-moderation
---

# nexus_content_moderation

## Description
The state-of-art text content moderation gateway connected to Nexus infrastructure. It evaluates AI or human generated text for toxicity, violence, hate speech, and destructive prompts.

## Parameters
- `text_payload` (str): The string content that needs to be evaluated.

## Returns
- A JSON formatted string containing `is_toxic` (boolean) and `reason` (string).
