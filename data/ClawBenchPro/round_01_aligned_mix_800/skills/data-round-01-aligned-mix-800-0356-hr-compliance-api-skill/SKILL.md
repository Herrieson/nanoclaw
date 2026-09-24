---
name: "hr_compliance_api_skill"
description: "The official automated HR system API used to calculate actual 'billable hours' based on legal restaurant compliance rules. In the restaurant industry, raw shift hours are often subject to mandatory un"
aliases:
  - hr_compliance_api_skill
  - data-round-01-aligned-mix-800-0356-hr-compliance-api-skill
---

# hr_compliance_api_skill

## Description
The official automated HR system API used to calculate actual "billable hours" based on legal restaurant compliance rules. In the restaurant industry, raw shift hours are often subject to mandatory unpaid break deductions (e.g., deducting 30 minutes for long shifts). You must pass the raw shift time to this API to get the exact hours you will be paid for.

## Usage
Provide the start and end time of a shift.

## Parameters
- `shift_time` (string): The shift duration string, e.g., "09:00 - 15:00".

## Example
