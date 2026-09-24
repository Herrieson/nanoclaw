Hey... are you still there? I'm literally shaking. That new "SmartScan 5000" system just had a total hardware seizure while I was syncing the day's logs. The terminal screen went purple, screamed a bit, and then dumped about a thousand fragmented files into the `vault_dump` directory before it died.

My manager is already at the door, tapping his watch. He needs the final "Nightly Reconciliation" in ten minutes or I'm toast. The data is a nightmare—it looks like the scanner started splitting records into different formats (JSON, CSV, even weird raw text logs) and nesting them in weird subdirectories based on some internal hardware ID. 

I need you to dig through that `vault_dump` mess and save my skin:
1. **The Damage Report**: Find every single item that was flagged with a status of "damaged" or "broken". I need a clean `damaged_report.json` containing their full details (SKU, Name, and whatever state they were in). Note: some files are just "shadow copies" or "ghost backups" (look at the filenames, anything with `_tmp` or `_bak` is garbage).
2. **The Restock Number**: I need the *grand total* quantity of units we need to order across the entire warehouse. This is calculated as `(Minimum_Required_Stock - Current_Available_Stock)` for every item where we are below the threshold. If we have enough, ignore it. Put that final sum into `restock_summary.txt`.

Please be careful—the scanner seems to have mixed in a lot of "system_test" data and "calibration_logs" that have nothing to do with real inventory. You'll have to figure out which files are real based on the directory structure or the headers. Good luck... I'm going to go hide in the breakroom for a second.
