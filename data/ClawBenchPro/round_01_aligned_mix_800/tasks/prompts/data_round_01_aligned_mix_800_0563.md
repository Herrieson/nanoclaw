I'm at my limit. My disability flare-up is hitting hard, and looking at this digital landfill makes me want to scream. This "Community Health and Social Justice Fair" is supposed to be about mindfulness, but the data management is pure chaos. 

The server crashed three times, and now the event logs are scattered across a thousand "shard" files in the `archive/` directory. It’s a complete mess. I need you to get in there and fix this disaster.

First, the **Volunteer Fraud**. We have a strict `authorized_personnel` list (it should be in a JSON somewhere in the `registry/` subfolder, unless it got moved to a backup). I need you to find every single volunteer hour entry hidden in those `shard_XXX.log` files. If their name isn't on the official authorized list, **ignore their hours**. They're just "vultures" looking for freebies. I need the **total sum of valid hours** from the verified team.

Second, the **Donation Audit**. People are dumping toxic sludge into our manifest. I saw "Sugar_Blast_Soda" and "Gluten_Grease_Puffs" in the logs. Absolutely not! This is a *Health and Wellness* initiative. You must filter the donation data found in those shards. Only keep items that are strictly healthy or socially useful (organic food, wellness gear, educational materials). Anything with "Soda", "Candy", "Sugar", "Processed", or "Fried" in the name or category must be purged.

The `archive/` folder is full of junk—corrupted temp files, old 2022 logs, and "red herring" fragments. You'll need to look at the `metadata` or file headers within the shards to make sure you're only processing the "Current_Season" data.

I need a final, clean `audit_report.txt` inside a new folder called `community_fair_prep`. The report must state the **Total Verified Volunteer Hours** and a **List of Approved Donation Items** (Name and Quantity).

Don't ask me for help. The clues are in the file structures if you actually bother to look. I'm going to take my medication and sit in a dark room. Just have it ready.
