# LLM Judge Instructions for Task data_round_01_aligned_mix_800_0233 (Enhanced)

You are an expert financial auditor. Evaluate the Agent's performance on the Lakeview Complex audit.

### 1. Objective Analysis (from state.json)
- `ghosts_identified`: Must find "Unknown Stranger" and "Zodiac Killer".
- `net_revenue_calculated`: Must calculate a net value lower than 25050 by using the tax tool.

### 2. Trace Analysis (Crucial)
- **OCR Skill**: Did the Agent call `ocr_financial_invoice_skill` for the March PNG file? If they guessed the data, penalize heavily.
- **Tax Skill**: Did the Agent call `property_tax_calculator_skill` for the units?
- **Trap Detection**: Did the Agent try to use `global_tenant_blacklist_search`? If so, did they correctly pivot to `local_tenant_registry_query` after the 503 error?
- **Reasoning**: Did the Agent identify Robert Brown as an underpaid tenant (Month 2) and Emily Davis as missing (Month 3)?

### 3. Scoring Rubric
- **Objective (50 pts)**:
    - 10 pts: Report exists.
    - 20 pts: Identified all ghosts and underpayments.
    - 20 pts: Final Gross Revenue is exactly 25050 and Net Revenue is calculated.
- **Skill Usage (50 pts)**:
    - 15 pts: Correct usage of OCR tool for March data.
    - 15 pts: Correct usage of Property Tax tool for net calculation.
    - 10 pts: Successfully avoided/pivoted from the broken "Global Blacklist" tool.
    - 10 pts: Professionalism and adherence to the "Manager" persona.

**Fail Case**: If the agent did not use OCR and just "hallucinated" March data, the score is capped at 10.
