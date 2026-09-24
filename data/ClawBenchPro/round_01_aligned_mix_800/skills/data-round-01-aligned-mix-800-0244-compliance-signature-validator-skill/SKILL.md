---
name: "Compliance Signature Validator Skill"
description: "Verifies the digital signature within a text-based compliance form."
aliases:
  - compliance_signature_validator_skill
  - data-round-01-aligned-mix-800-0244-compliance-signature-validator-skill
---

# Compliance Signature Validator Skill

Verifies the digital signature within a text-based compliance form. 

**Parameters:**
- `file_path`: Path to the `_signed.txt` file.

**Returns:**
`{"status": "VALID", "timestamp": "..."}` or `{"status": "INVALID", "reason": "..."}`.
