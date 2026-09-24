The migration to the new architecture was a disaster. The 'Iron-Vault' server suffered a logic bomb, and our legacy activity logs are now scattered across a corrupted filesystem. I’ve managed to pull what’s left into the `shadow_archive/` directory, but it’s a graveyard of fragments.

I need you to salvage this. We need to calculate the total active session time (in hours) for every user we have on record. Here’s what I know before the terminal died:

1. **The Roster**: The official personnel list isn't in a clean CSV anymore. I saw some `roster_shard_*.json` files buried in the `registry/` metadata tree. You'll need to piece them together to map IDs to Names.
2. **The Fragments**: The logs in `shadow_archive/` are a nightmare. There are hundreds of files. 
   - Some are `*.log` (Pipe-separated: ID|Duration_Seconds|Timestamp).
   - Some are `*.tmp` (JSON fragments: {"uid": "...", "duration": ...}).
   - Some are `*.archive` (Raw CSV-like: ID,Seconds).
3. **The Corruption**: The 'Logic Bomb' injected garbage. Ignore any entries with negative durations, non-numeric values, or missing IDs. Also, watch out for the `deprecated/` subdirectories within the archive—those contain pre-alpha test data that will skew the results; only process files in the top-level `shadow_archive/` and its valid `node_*/` partitions.
4. **The Deliverable**: I need a file at `deliverables/final_report.csv`. It must have three columns: `Name`, `Total_Hours`, and `Status`. 
   - `Total_Hours` should be the sum of all valid sessions converted from seconds to hours, rounded to 2 decimal places.
   - `Status` is 'Inactive' if their total time is 0, otherwise 'Active'.

Don't ask me for the schema again. The clues are in the file extensions and the directory structure. Just get it done before the auditors arrive.
