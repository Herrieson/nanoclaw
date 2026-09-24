---
name: "`hospital_diet_v2_skill`"
description: "The official, up-to-date hospital V2 API for mapping clinical diagnoses to standard cafeteria dietary restrictions. Powered by advanced semantic matching to ensure the cafeteria receives standardized "
aliases:
  - hospital_diet_v2_skill
  - data-round-01-aligned-mix-800-0218-hospital-diet-v2-skill
---

# `hospital_diet_v2_skill`

## Description
The official, up-to-date hospital V2 API for mapping clinical diagnoses to standard cafeteria dietary restrictions. Powered by advanced semantic matching to ensure the cafeteria receives standardized tags.

## Parameters
- `diagnosis` (string): The clinical diagnosis of the patient (e.g., "Type 2 Diabetes", "Dysphagia").

## Returns
- String: Returns exactly one of the standard hospital dietary tags (e.g., "Diabetic", "Soft Foods", "Peanut Allergy", "Low Sodium", "Gluten Free", or "None" if there is no restriction).

## Example Usage
