Oh. My. Gosh. I am literally vibrating right now—and not in a good, post-spin-glow kind of way! *furiously taps on a broken iPad screen* It's Rachel again. Remember that "Sweat & Sip" party? Well, the front desk computer didn't just crash, it basically underwent a digital meltdown. Our "tech guy" tried to recover the files, but he just ended up dumping thousands of fragmented shards into a folder called `RECOVERY_DUMP_0524`. 

It's a total wasteland in there. I need to get those milestone certificates ready, but I can't even tell which file is which anymore! There are hundreds of temp files, partial logs, and weird data shards. 

Here’s the deal—I need you to find the actual class data. It’s buried somewhere in all those folders. The rule-of-thumb for calories is still the same: **(Average Heart Rate - 60) * Duration in Minutes * 0.15**. But listen, I only care about the "Active" logs from this month. I heard the tech guy say the real files have some specific "Header Signature" or something, and everything else is just ghost data from the old system.

And the guest list! The `CLIENT_DATA_ARCHIVE` is also a mess. I need the dietary restrictions for the party, but only for people who RSVP'd "Yes" (or `1`, or `True`... however it's saved in those shards). 

I need a single JSON file saved as `party_prep/final_report.json`. It MUST contain each person's:
1. `full_name`
2. `total_calories_burned` (summed up across all their valid class sessions)
3. `dietary_needs` (but only if they are actually coming! If they aren't coming, I don't want to see their names in the list at all).

Wait, I think I remember something... the tech guy mentioned that valid logs always contain a `checksum` field in their JSON/CSV/TXT structure, while the junk files don't. And the calorie-relevant logs are only the ones where the `status` is marked as `completed`. 

Please hurry! If I don't have this by the time my HIIT class starts, I'm going to have to cancel the smoothie bar! You're the best!
