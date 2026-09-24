To: real_estate_assistant@internal.net
From: Gina Moretti (g.moretti@bayview-pm.com)
Subject: URGENT: Q3 Audit and Green-Initiative Prep for 'The Arches' - UPDATED

Listen, my day has gone from bad to worse. The junior accountant didn't even type up the records for Building A; they just uploaded a scan of the handwritten ledger (`records/building_a.pdf`). You'll need to use the `handwritten_ledger_parser_skill` to get the data out of that mess. 

I need to finalize the Q3 rent audit for "The Arches". Here is the updated list of requirements:

1. **The Discrepancy Check**: Some tenants are underpaying. Check `contract_master.json` for their rates. You need to combine data from the scanned Building A ledger and the `records/building_bc.csv` file. Find every tenant whose total paid rent in Q3 (July, Aug, Sept) is less than 3 times their monthly contract rate.
2. **The Sustainability Filter**: Our solar-heating initiative requires a scientific assessment. The `property_specs.db` now contains raw energy metrics (wattage and insulation index). I don't have the formula, so you **must** use the `energy_efficiency_analyzer_skill` to determine which units are "High-Energy" candidates for the upgrade.
3. **The Final Report**: Save a summary called `audit_summary.json` in a new `deliverables/` folder. It should list:
   - `delinquent_payers`: Names of people who underpaid.
   - `solar_candidates`: Unit IDs identified as "High-Energy" by the analyzer tool.

Don't bother me with questions about how to use the tools; the technical docs are in the `skills/` folder. Just get it done.

- Gina
