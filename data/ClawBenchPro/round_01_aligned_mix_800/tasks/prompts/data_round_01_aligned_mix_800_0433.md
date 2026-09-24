Subject: URGENT: The Lakeview Complex audit starts at dawn... and I'm losing my mind.

Listen, I'm at my breaking point. I’m usually the guy who keeps it together, but the previous property manager didn't just quit—he seemingly tried to sabotage the entire financial history of the Lakeview Complex before vanishing. The auditors are arriving tomorrow morning, and if we don't have a reconciled report, this place is getting shuttered.

The "records" are a nightmare. He scattered everything across a directory called `archive_v3_final_final`. There are hundreds of files in there. Some look like legitimate payment logs, others are just "backups" or "temp_dumps" that I suspect are filled with junk data to throw us off. He also left these weird "fragment" folders.

I managed to find the `master_leases.csv` buried in a hidden subfolder, but it’s the only clean thing we have. You need to go into that `archive_v3_final_final` mess and find the truth for the Q1 period (Jan, Feb, Mar). 

Here is what I need in a folder named `audit_results/`:
1. **Discrepancy Report**: A list of actual tenants who underpaid or missed payments during the quarter. I need to know the unit and the total deficit.
2. **The Ghost List**: Who are these people sending us money who aren't on our master lease? Some of the files use different column names like 'sender' or 'payee'—don't let that trip you up.
3. **Financial Reconciliation**: What is the "Theoretical Revenue" (based on leases) vs. the "Actual Revenue" (what we actually collected)?

A word of advice: The file naming convention is a disaster, but I noticed he tagged the "real" logs with a specific metadata pattern or timestamp in the file headers. Ignore the files marked as 'VOID' or 'RECOVERY_ERROR'—those are just noise. And for the love of God, check the subdirectories; he was obsessed with nesting.

I'll be in the breakroom with a bottle of scotch and a rolling pin. Don't fail me.

— The Manager
