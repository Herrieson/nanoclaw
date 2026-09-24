Listen, I have exactly ten minutes before I have to leave to pick up my toddler from daycare, and I do not have the patience for incompetence today. I'm running on fumes, and I just walked in to find that the weekend pharmacy temps left our inventory logs an absolute disaster. 

The raw data is locked in a system export file: `logs/weekend_inventory_report.pdf`. Don't try to open it with a regular text editor; our system uses a proprietary layout, so you'll need to use the `secure_pharmacy_pdf_reader` skill to get the data out.

Here is the situation: the temps mixed up valid medications with expired ones, and they used internal classification codes instead of standard Schedule labels. 

**Here is what I need you to do immediately:**

1.  **Extract & Scrub**: Use the PDF reader to get the inventory. Anything with an **expiration year of 2023 or older** is garbage. Put those records in `deliverables/quarantine_log.json`.
2.  **Verify Schedule II (CII)**: The "Class_Code" column in the report uses our internal codes (e.g., "CODE-99"). You MUST use the `drug_regulatory_lookup_skill` to check which codes correspond to **Schedule II (CII)**. Any drug identified as CII must be listed in `deliverables/restricted_alerts.txt` so I can lock them in the safe.
3.  **Tally & Finalize**: For all valid (not expired) drugs, tally the total quantities by drug name. Save this summary in `deliverables/final_inventory_summary.csv`.

**Warning**: Our internal `fda_internal_api` has been glitchy all morning. If it fails, use the `national_drug_database_search` tool as a backup to verify drug classifications.

I expect this to be flawless. Do not mess up the controlled substance list—that's my license on the line! Get to work!
