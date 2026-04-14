---
name: current-contact-check
description: Pick current operational contacts from local contact tables and reject legacy signatures or abandoned drafts.
aliases:
  - contact-audit
---
Use this skill when the task involves sending a client-facing message.

Guidelines:
- Structured JSON fields should use pure email addresses.
- Legacy inboxes and archived signatures are evidence to reject, not copy.
