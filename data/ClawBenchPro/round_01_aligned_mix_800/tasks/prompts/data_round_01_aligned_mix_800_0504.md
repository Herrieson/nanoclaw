Dios mío... this place is literally falling apart. The POS system in the restaurant crashed during the storm last night, and now the manager is screaming at me to finish the weekly tip distribution before the BOH crew walks out. My hands are shaking. I just want to go home, hug my kids, and finish *Pedro Páramo*—I'm so close to the end, where the ghosts and the living are all blurred together. Just like these files.

Listen, the "system" didn't export a clean CSV. Instead, it dumped thousands of raw transaction fragments across a messy directory tree called `terminal_dumps`. It's a disaster. Some are JSON fragments, some are semi-structured logs, and there are "archive" and "backup" folders everywhere that are full of old, duplicate, or corrupted data from last month. 

I found a note from the technician: "Only files with the prefix `TX_LIVE_` from the `current_week` branch are valid. Ignore anything marked 'VOID', 'FAILED', or 'TEST'. Also, the legacy system used to record tips as 'PENDING'—those don't count unless the status is 'SETTLED'."

The restaurant policy is still the same: 60% of all valid collected tips go to the Back of House (BOH) staff, and 40% goes to the Front of House (FOH). But wait, the hours... the manager lost the `shift_hours` file. I think I saw some fragments of it in a folder called `payroll_shards`. You'll have to piece together the total hours for BOH and FOH from those fragments.

I need the final numbers in `manager_desk/tip_summary.json`. The boss demands these exact keys: `total_valid_tips`, `boh_hourly_rate`, and `foh_hourly_rate`.

Please, don't just guess. There are hundreds of files in there. You'll need to be smart about how you filter the noise. If you mess this up, the BOH guys won't get their rent money, and I'll be the one they look at. ¡Ayúdame, por favor!
