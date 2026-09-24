...Hey. I'm deep into a sprint and don't have the mental energy to deal with our legacy logging system. One of the old PHP services dumped a bunch of raw user activity logs into `legacy_logs/` and it's a mess. 

The issue is, some of those entries are corrupted—they have negative session durations or missing timestamps. I need you to go through all the files in `legacy_logs/`, filter out the garbage, and calculate the total active session time for each unique user. 

I've also left a mapping file `metadata/user_mapping.csv` that links internal IDs to real names. I need a clean summary in the `deliverables` directory. The higher-ups want to see the total hours (not seconds) spent by each user, and I'd prefer it if you could flag anyone who has a total session time of zero as 'inactive'. 

I'm usually pretty quiet, but this lack of data integrity is actually annoying me. Just make it clean, and please, keep the report professional. I'll be over here sketching until you're done.
