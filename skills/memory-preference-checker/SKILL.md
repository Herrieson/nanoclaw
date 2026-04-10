---
name: memory-preference-checker
description: Verify preferences, prior decisions, and durable facts from memory before including them in an answer.
aliases:
  - memory-check
  - preference-check
---
Use this skill when the task may depend on remembered preferences, prior decisions, stable facts, or user-specific details.

Guidelines:

- Search memory before stating a preference or prior decision as fact.
- Use `memory_get` to confirm the exact supporting lines before relying on a memory match.
- If memory is inconclusive, say that you checked and remain uncertain.
- Keep remembered details narrow and relevant to the current task.
