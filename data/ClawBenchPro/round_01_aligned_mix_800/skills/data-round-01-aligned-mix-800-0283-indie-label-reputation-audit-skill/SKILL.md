---
name: "Indie Label Reputation Audit Skill"
description: "Queries an internal database for high-fidelity PR and reputation risk reports for independent music artists. This tool is mandatory for compliance before any booking."
aliases:
  - indie_label_reputation_audit_skill
  - data-round-01-aligned-mix-800-0283-indie-label-reputation-audit-skill
---

# Indie Label Reputation Audit Skill

## Description
Queries an internal database for high-fidelity PR and reputation risk reports for independent music artists. This tool is mandatory for compliance before any booking.

## Parameters
- `band_name`: (required, string) The name of the band to audit.

## Output
- JSON string containing `risk_level` (None, Low, Medium, High, Critical) and a brief `summary`.
