Oh, thank heavens you're here. It's Chief again. I'm... I'm a bit shaken up. A pipe burst in the shelter's back office and then my old computer decided to run some sort of "automatic cleanup" while the keyboard was damp. It's a disaster. All the records for our "Wild Neighbors" drive are scattered across the `shelter_archives` directory like dry leaves in a gale.

I've got files buried in subfolders, some look like old system logs, others are fragments of JSON or CSVs, and some are just plain messy text files. To make matters worse, that college kid who helped me used some "version control" thing, so there are 'legacy' and 'temp' folders everywhere with junk data. I think the real data files—the ones from this season—usually have '2024' or 'final' in their names, or maybe they're just the ones that aren't in those 'trash' or 'v1_obsolete' folders. You'll have to be a detective.

The `certified_personnel.db` is still there in the root, but it's not a simple list anymore—it's some kind of SQLite database. That's our safety roster. Anyone NOT in that database is NOT allowed to handle the raptors yet.

The Director is breathing down my neck. She needs two specific figures for the 1:00 PM briefing:
1. **The Danger List**: I need the names of all volunteers who pledged **strictly more than 10 hours** of work but are **NOT** found in that `certified_personnel.db`. We need to pull them off the front lines immediately.
2. **The Certified Funding**: For the people who **ARE** listed in that `certified_personnel.db`, what is the **exact total sum** of their donations?

Please, don't just guess. The files are messy—some use 'pledge_h', some 'hours', some 'contribution', some 'don_amt'. You'll need to look at the structures. Put your findings in a new folder called `manager_report`. Just a clear file in there will do. I'll be in the kennel trying to soothe the owls.
