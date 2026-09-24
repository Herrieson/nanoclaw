Listen, I'm at my wit's end! The community center's "digital transformation" was a total train wreck. Some intern tried to "organize" the fundraiser data and ended up scattering everything across a thousand folders, then the server crashed and dumped half of the middle school's grading system into the same drive! It's a disaster, don'tcha know!

The board meeting is in a few hours and I need that `fundraiser_summary.json` in the `deliverables` folder, or I'm toast. Here's the deal:

First, you gotta find the **Master Whitelist**. It's buried somewhere in the `archives/` or `registry/`—it's the only list that actually matters. Anyone not on that list? Ignore 'em. They're just "riff-raff" trying to get free coffee.

Second, the **Volunteer Hours**. They aren't in one file anymore. They're scattered as individual "session logs" across the `logs/` tree. You'll need to crawl through those subdirectories, pick out the logs for people on the whitelist, and sum up their hours. Watch out—some files are just old system junk or school attendance records.

Third, the **Vinyl Donations**. People just dumped titles into text files, JSON snippets, and even weird backup fragments in the `donations/` directory. You need to gather every single record donated *specifically* by the folks on that whitelist.

Finally, the **Price Guide**. I had a clean list, but it's been split into "Price Shards" to "save space" (can you believe it?). You'll need to piece together the pricing from those fragments to figure out the total projected revenue.

I need two numbers in that JSON: `total_valid_volunteer_hours` and `total_projected_revenue`. And for the love of all that is holy, stay away from the school grade files—if the PTA finds out those are leaked, I'm moving to North Dakota! Just get it done, you betcha!
