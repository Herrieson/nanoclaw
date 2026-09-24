Listen, I don't care if the server room is literally on fire—I need that refund report NOW or we're both out of a job! That West African art showcase was supposed to be the highlight of the decade, and instead, it's a PR nightmare. The grid failure didn't just kill the lights; it corrupted half our logging systems.

I’ve had the interns dump everything they could scavenge into the `archived_logs` directory. It’s a complete wasteland in there. Files are scattered across deep subdirectories, named with cryptic timestamps, and half of them are just junk or "pre-incident" noise. 

You need to find every account affected by the outage and calculate their compensation. My rules are final:
1. Base credit for any outage: $50.
2. If the outage duration was strictly *more* than 4 hours: $100 total (replaces the $50).
3. Special Art Bonus: If their report mentions an "art exhibition", "gallery", "painting", or "sculpture", tack on an extra $200. This is *cumulative* with their duration-based credit.

The data is a mess. I saw some JSON shards, some weird semi-structured log files, and a bunch of CSV fragments. Some files have a `.tmp` or `.bak` extension—ignore those, they’re just corrupted echoes. Only look at the files that don't have those "temporary" extensions. And for heaven's sake, don't miss the cross-reference IDs in the `metadata_mapping` folder if you find any "System-Alpha" logs; they don't use account IDs directly, they use internal GUIDs that you'll need to map back to the real account numbers.

I want a clean `refund_report.json` in the `deliverables` folder. It must be a flat mapping of `account_id` to the `total_refund_amount`. Also, include a `"total"` key at the root representing the sum of all refunds. 

If you mess up one single calculation, finance will reject the whole batch. Get to work.
