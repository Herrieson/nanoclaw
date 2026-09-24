Listen, I absolutely do not have the patience for this today. I’m spinning my Claddagh wedding ring so hard it’s practically leaving a bruise on my finger. Between my toddler throwing a tantrum this morning and the absolute incompetence of the IT department at this non-profit clinic, my blood pressure is through the roof.

I need to submit the DEA audit report for missing narcotics and medications, but our new "cloud-native" inventory system is a fragmented nightmare. Every time I ask for a simple report, the developers just tell me "the data is in the lake." I don't want to dive into a lake! 

I did the physical counts myself, but comparing it to the system's expected baseline is practically impossible by hand now. Here is what you need to navigate this disaster:

1. They left all the historical inventory snapshots dumped in `inventory/base/`. I only care about the current audit period. You have to open those files and find the one whose internal metadata `audit_period` explicitly says `"2023-11"`. That's our starting pill count.
2. The transaction logs are scattered across dozens of daily folders in `transactions/`. And guess what? The staff are idiots. They constantly cancel or fail transactions. You must ONLY tally transactions where the `status` is exactly `"completed"`. Also, notice the `action` type: a `"dispense"` means pills left the pharmacy, but a `"restock"` means pills were added back to our inventory.
3. Because the pharmacy is huge, my interns did the manual physical counts by zones. The data is in `physical_counts/`, split into several CSV files. You'll need to aggregate the totals for each drug yourself.
4. To make matters worse, all these system files use internal `drug_id`s instead of human-readable names! You'll need to cross-reference them with the master list in `reference/drug_catalog.csv`. I don't speak robot, I need actual drug names in the final output.

Calculate the expected inventory (Start + Restock - Dispense) and compare it against the aggregated physical counts. If the physical count is *lower* than expected, someone has been stealing or losing pills. 

I don't want a messy terminal output. I want a clean, formal JSON dictionary saved exactly at `reports/missing_drugs.json`. The keys must be the human-readable drug names, and the values must be the exact integer amount of missing pills. Do NOT include drugs that balance perfectly. I only want the ones in deficit.
