---
name: "Optical Expense Analyzer Skill"
description: "Calculates the final reportable cost for optical items, applying local sustainability subsidies and carbon tax credits."
aliases:
  - optical_expense_analyzer_skill
  - data-round-01-aligned-mix-800-0266-optical-expense-analyzer-skill
---

# Optical Expense Analyzer Skill

## Description
Calculates the final reportable cost for optical items, applying local sustainability subsidies and carbon tax credits. 

## Parameters
- `base_cost`: (required) Float or String. The initial price.
- `item_code`: (required) String. The optical product code (e.g., 'OPT-001').
- `category`: (required) String. Must be 'Sustainable' or 'Standard'.

## Returns
A JSON string containing the 'final_cost' after applying a 10% discount for 'Sustainable' items.
