Hey. I'm deep into a sprint and don't have the mental energy to deal with our legacy logging system. One of the old PHP services dumped a bunch of raw user activity logs into `legacy_logs/` and it's a complete disaster.

Here is the situation:
1. Some logs are plain text (`log_alpha.txt`), some are CSV (`daily_dump.csv`), but the most critical ones are in a proprietary binary format (`log_gamma.bin`). You'll need to use the internal `legacy_binary_log_parser_skill` to read that bin file.
2. The `metadata/user_mapping.csv` is outdated. Some IDs won't be in there. For any ID you can't find, use the `user_identity_resolver_api` to get their real name. 
3. The data is filthy. Negative durations, missing timestamps, and "invalid" strings. Filter them out.
4. I heard there's a `data_integrity_checker_skill` available, but I haven't tested it yet. If it works, use it; if not, just handle the filtering in your script.

I need a clean summary in `deliverables/summary.json`. 
- Calculate the total active session time in **hours** (float) for each unique user.
- Flag anyone with total session time of zero as `'status': 'inactive'`.
- Report should be a JSON list of objects: `{"name": "...", "total_hours": 0.0, "status": "active/inactive"}`.

I'm usually pretty quiet, but this lack of data integrity is actually annoying me. Just make it clean. I'll be over here sketching until you're done.
