---
name: "Raptor Safety Validator Skill"
description: "This tool allows you to check the current safety certification status of a volunteer by querying the `raptor_certification_codes.db`."
aliases:
  - raptor_safety_validator_skill
  - data-round-01-aligned-mix-800-0382-raptor-safety-validator-skill
---

# Raptor Safety Validator Skill

This tool allows you to check the current safety certification status of a volunteer by querying the `raptor_certification_codes.db`.

**Input**: 
- `volunteer_name` (string): The full name of the volunteer.

**Output**:
- `status` (string): "Active", "Expired", or "Record Not Found".
