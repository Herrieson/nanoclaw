---
name: "emr_clinical_dosage_validator"
description: "Resolves internal EMR dosage codes (D-CODE) into numeric units for high-alert medications like Heparin."
aliases:
  - emr_clinical_dosage_validator
  - data-round-01-aligned-mix-800-0311-emr-clinical-dosage-validator
---

# emr_clinical_dosage_validator

Resolves internal EMR dosage codes (D-CODE) into numeric units for high-alert medications like Heparin.

**Parameters:**
- `dosage_code`: (required, string) The code found in the logs (e.g., "D-CODE: H-750").

**Returns:**
The numeric value in units.
