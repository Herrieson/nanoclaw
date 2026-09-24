Look. My desktop is an absolute trash fire right now and I don't have the patience to sort it out. I've got to drop the kid at daycare in twenty minutes, and then I'm hitting the squat rack.

I dumped a bunch of my music export logs and the auto glass supplier invoices from the shop into the `raw_dump` folder. They're all mixed up because I just didn't care at the time. 

Here's what I need you to do:
First, find my lifting playlist. I synced music from three devices (phone, laptop, tablet), so the formats are all over the place (JSON, CSV, XML). I only want the energetic tracks—anything with a BPM strictly over 120. Put the exact names of those tracks in a file called `workout_playlist.txt` inside a new `results` folder, one track name per line.
One catch: the laptop exports don't use BPM, they use this weird 'Energy Code' my DJ friend set up. He left a cheat sheet in the `manuals` folder somewhere mapping codes to BPM. Oh, and ignore any files inside directories named `corrupted` or `recycle_bin`, those are broken duplicates that will ruin the playlist!

Second, the shop needs to know exactly how much we spent on windshield replacements last month. I dumped the invoices from both branches in the `invoices` folder. 
- Branch North uses text files.
- Branch South uses JSON files, but their system is dumb and doesn't include the item prices! You'll have to look up the prices using the master parts catalog buried somewhere in the dump.
- **CRITICAL**: We only want the cost of the actual windshield glass. My partner started categorizing part numbers recently: actual windshield glass ALWAYS has a part number starting with `GLS-WND-`. Everything else (like `ACC-` for wipers, `CHM-` for adhesives, or `GLS-SID-` for side glass) should be ignored.
- Only count invoices where the status is `PAID` or `COMPLETED`. Do NOT count `VOID`, `CANCELLED`, or `PENDING` invoices.

Calculate the total cost (Unit Price * Quantity) for all valid windshield replacements, and drop that final number (just the number, rounded to exactly 2 decimal places) into `windshield_costs.txt` in the same `results` folder.

Don't give me a whole presentation. Just get the files made so I can text my boss the number and get to the gym.
