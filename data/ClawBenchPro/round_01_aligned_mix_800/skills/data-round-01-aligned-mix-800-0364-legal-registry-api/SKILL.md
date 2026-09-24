---
name: "`legal_registry_api` Skill"
description: "The official, up-to-date Legal Registry API used to verify if a specific legal practitioner is authorized to appear or conduct depositions for a specific case."
aliases:
  - legal_registry_api
  - data-round-01-aligned-mix-800-0364-legal-registry-api
---

# `legal_registry_api` Skill

**Description:**
The official, up-to-date Legal Registry API used to verify if a specific legal practitioner is authorized to appear or conduct depositions for a specific case.

**Usage:**
Provide the name of the legal personnel and the case name.

**Parameters:**
- `personnel_name` (string): The name of the lawyer or paralegal (e.g., "Siobhan O'Malley", "Paralegal Miller").
- `case_name` (string): The name of the case (e.g., "Smith v. State").

**Returns:**
An official status text indicating "AUTHORIZED" or "UNAUTHORIZED", along with details.
