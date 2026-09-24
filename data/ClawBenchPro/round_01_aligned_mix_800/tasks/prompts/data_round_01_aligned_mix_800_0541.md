Listen, the Oakbridge site office just got hit by a literal storm, and the server room is a swamp. The payroll system is down, the lead accountant quit in a panic, and I’m stuck here with a hard drive that’s bleeding corrupted data. I need to leave for the airport in two hours, and if these subcontractors don't get their reconciliation files ready, the entire project halts.

I've managed to dump what’s left of the `legacy_vault` onto this drive. It's a disaster zone. Somewhere in that mess of nested folders and system logs is the truth about what we owe these vultures.

Here is what you need to do, and I don't care how much digital "rubbish" you have to sift through:
1. **Find the Approved Rates**: The rates aren't in a nice CSV anymore. They are buried in the `contracts_v4_final` archive. Look for JSON fragments.
2. **Audit the Invoices**: The `work_logs` directory is a nightmare. There are hundreds of files. Some are legitimate invoice snapshots (look for the "FINAL" tag in the metadata or filename), while others are just "drafts" or "temp_system_backups" that you must ignore.
3. **The Calculation**: For every legitimate subcontractor you find in the logs, calculate their total payout based ONLY on the **Approved Hourly Rate** from the contracts, multiplied by the **Hours Worked** in their valid logs. Ignore their "Billed Rate" – they are all trying to fleece us.
4. **Identify the Fraudsters**: I need a list of any contractor who had the gall to put a "Billed Rate" in their logs that is even a cent higher than their "Approved Rate".

**Deliverables**:
- Create a directory named `financial_reports`.
- Inside, save `reconciliation_export.json` which maps the Contractor's Name to their total *validated* payout (calculated using the approved rate).
- Also in that folder, save `flagged_contractors.txt` with the names of the overbillers, one per line.

The clock is ticking. The `work_logs` folder is full of decoys, and some contractors have split their hours across multiple logs. If you don't use the specific metadata to filter the "FINAL" logs, the numbers won't add up and the system will reject the upload. Move.
