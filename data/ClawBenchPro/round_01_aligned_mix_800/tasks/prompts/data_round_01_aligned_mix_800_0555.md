Dude, I am literally hiding in the supply closet right now! My manager is on a total rampage. 😭

Listen, Neon Galaxy MD is totally chaotic lately. The previous janitor quit and dumped all the lost and found records from his shifts into the `logs/` directory. It's a complete nightmare. He generated logs for every single week, but my manager specifically yelled at me to ONLY compile the lost and found report for **Week 42** (`logs/week_42/`). Ignore all other weeks or you'll ruin the stats!

Here is the deal:
Inside those Week 42 log files, there are thousands of lines of useless patrol garbage. You have to hunt down the lines that contain the tag `[LOST & FOUND]`. The previous guy had a habit of writing them like this: `... [LOST & FOUND] ITEM: <the item> | OWNER: <the owner>`. 

My manager wants me to cross-reference these owners to see if any of them are our elite VIPs. But guess what? We don't just have a "VIP list". You have to go into the `db/` folder. There's a `customers.csv` (which has the `customer_id` and `full_name`) and a `memberships.json` (which links `c_id` to their `level` and `status`). A customer is ONLY considered a VIP if their `status` is exactly `"active"` AND their `level` is 4 or higher (like 4, 5, etc.). 

If a VIP lost something, I need you to create a `vip_alerts.json` file inside a new `deliverables/` folder. Just make it a JSON list of objects containing the keys `"vip_name"` and `"item"`. 

Also, we get so much garbage left behind. My boss wants a total count of the "junk". A lost item is considered "junk" if the `OWNER` extracted from the log is empty, or if it says "NONE", "N/A", "UNKNOWN", or "NULL" (ignore case and any surrounding spaces). Please put this total integer count into a file called `junk_count.txt` inside that same `deliverables/` folder.

Please write a script to do this and save me! If I poke my head out now, I'm fired. Thank you!
