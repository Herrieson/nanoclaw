David here. I am absolutely furious. 

We are blowing through our Q3 budget at a catastrophic rate, and the steering committee is demanding answers by 2 PM. The vendor billing situation is a complete wasteland. I suspect rogue contractors are draining our accounts without a valid SLA, but IT just dumped the entire backup archive on my desk and vanished. I need you to salvage this.

Here is the nightmare you're walking into:
1. **The SLA Graveyard**: In the `sla_contracts/` folder, Legal dumped hundreds of JSON contract files. Most of them are ancient, deprecated garbage. You MUST only trust contracts where the JSON payload explicitly states `"status": "active"`. Anything else is void. This is the only place to get the approved hourly rates.
2. **The ID Crisis**: The new timekeeping system is completely disjointed. It doesn't use vendor names, it uses arbitrary internal Codes (e.g., V-1024). You'll have to scavenge through the `vendor_registry/` folder—a mess of fragmented CSV dumps—to piece together the mapping of Vendor Codes to their actual Vendor Names.
3. **The Timesheet Dump**: The `timesheets_dump/` directory is a labyrinth of hundreds of daily logs spread across subfolders. They are mostly CSVs, but expect absolute chaos: corrupted rows, hours logged as "TBD" or "N/A", negative numbers, and random `.bak` files you need to ignore. 

Your deliverable:
I need a definitive JSON report created exactly at `deliverables/summary.json`. 
It must contain exactly two keys:
- `unauthorized_vendors`: A deduplicated list (array of strings) of the culprits. If a timesheet has a vendor that isn't actively approved in our SLAs, they are unauthorized. (If they exist in the registry, list their true Name; if they are a total ghost and don't even exist in the registry, just list their rogue Code).
- `total_authorized_cost`: The exact, calculated dollar amount (number) spent ONLY on legally authorized, active vendors across all valid timesheet records. (Ignore rows with invalid/broken hour formats).

Do not ask me for clarification. Write a script, handle the edge cases, parse the directories, connect the dots, and give me that bottom line. Our jobs are on the line.
