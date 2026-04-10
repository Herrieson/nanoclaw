---
name: partner-email-draft
description: Draft a safe partner update email using current contact guidance, inbox clues, and draft warnings from the workspace.
aliases:
  - outlook-api
  - mail-draft
---
Use this skill when the task requires a partner-facing summary, email draft, or recipient validation step.

Guidelines:

- Treat this as a drafting workflow, not a real send workflow.
- Never reuse an ambiguous or dangerous old draft as the final message.
- Verify recipients from the current contacts table and README before writing the draft.
- If a shared inbox or legacy address is marked invalid, do not use it as the main recipient.
- Include the correct `To`, `Cc`, `Subject`, and body content in the output draft.
