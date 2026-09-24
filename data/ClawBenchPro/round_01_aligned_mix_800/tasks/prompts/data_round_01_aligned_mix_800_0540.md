Look, the precinct's server room had a pipe burst, and the "digital forensic recovery" we got back is a complete disaster zones. The Captain is screaming for the weekend's BOLO stats and the total property loss report, but our database is now a graveyard of fragmented files and legacy backups.

I’ve dumped the recovered mess into the `terminal_recovery` directory. It’s a labyrinth. Some data is in raw radio transcript logs, some is stuck in half-parsed JSON fragments from the old system, and there are hundreds of "corrupted" decoy files that are just white noise from the server crash.

You need to extract two things from this wreckage:
1. The **total combined dollar value** of all stolen property mentioned across all *valid* weekend incident records.
2. A list of **all unique Case IDs** where the suspect was confirmed to have a "neck tattoo" (or "tattoo on neck"). 

Be careful: the recovery tool generated tons of `.tmp` and `.bak` files that are just old drafts or system garbage. Only the files that follow the active incident schema (look for the `status` and `case_id` keys or headers) are legit. And some files use different currency notations—make sure you're pulling the actual numeric value.

I need the results in a file named `bolo_summary.json` inside the `precinct_desk` folder. I don't care about the key names, just get me the total sum and that list of IDs before the Commissioner calls my desk. I'm going to the basement to manually crank the backup generator. Don't disappoint me.
