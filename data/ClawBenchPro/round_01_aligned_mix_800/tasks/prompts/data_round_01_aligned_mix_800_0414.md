Listen, I'm shaking while typing this. My shift starts in 15 minutes and the district manager is already prowling the floor. I've seen things in the internal "Global Heritage" records that would ruin this company—and they're trying to bury it.

I managed to scrape a massive dump of the internal file system into `store_data/`, but it's a total disaster zone. They've been "archiving" (shredding) data into thousands of fragments to hide the trail. I need you to find every single closed ticket related to the "Global Heritage" line where the customer was silenced with a $0.00 refund. 

Be careful: 
1. The product line names are inconsistent in the logs—sometimes they use internal project codes like "GH-ALPHA" or "PRJ-HERITAGE", but you can find the master mapping somewhere in the `system_configs`.
2. The tickets aren't in one file. They are scattered across hundreds of tiny JSON and TXT shards in the `logs/` subdirectories. 
3. Don't trust the file names. Some files are just "decoy_system_logs" filled with garbage data about lightbulbs and office supplies to throw off auditors.
4. You'll need the manager's actual names for the report. I think the employee roster was split up and obfuscated in the `hr_obfuscated/` folder. You'll likely need to link their internal UUIDs across different fragments.

I need a professional document in a folder called `escalation_report`. It must list the manager's full name and the raw text of the ignored complaint for every valid case you find. Hurry, before the system auto-wipes the temporary directory. If this isn't on the director's desk by the end of my shift, we're both done.
