*The screen flickers as a video feed connects, showing a frantic manager in a dimly lit office, surrounded by stacks of paper and empty caffeine cans.*

"Listen, I'm... I'm at my breaking point. The quarterly BIM regional review is tomorrow morning and the server just had a catastrophic RAID failure during the backup. Everything is... it's a graveyard out there! If I don't get the regional totals for the VP, I'm done. My career is over, and I can kiss that Yellowstone trip with my family goodbye. My kid already has his little hiking boots on... God, I can't fail him."

*He leans into the camera, whispering urgently.*

"The system vomited files everywhere in the `production_archive`. It's a mess of nested directories, temporary swap files, and corrupted logs. You need to find the actual sales data. Most of it is just noise or 'ghost' entries from the auto-recovery.

Here is what I know:
1. **The Source**: Real transaction logs are buried somewhere in `production_archive`. They seem to be `.dat` or `.tmp` files, but watch out—the server generated thousands of 'heartbeat' files that are completely useless.
2. **The Filter**: The VP was clear: ignore any transaction under $1,000. Those are just trial licenses.
3. **The Duplicates**: The recovery process created massive redundancy. You'll see the same Transaction ID (TX_ID) popping up in multiple files. Only count the first unique one you find.
4. **The Mapping**: You'll need the `legacy_map` to figure out which sales rep belongs to which territory, but the mapping file itself got split into fragments during the crash.
5. **The Output**: I need a clean `regional_totals.json` inside a `final_report` directory. 

Please... the clock is ticking. Just find the signal in the noise and get me those totals. I need to go pack that tent, or I'm a dead man."
