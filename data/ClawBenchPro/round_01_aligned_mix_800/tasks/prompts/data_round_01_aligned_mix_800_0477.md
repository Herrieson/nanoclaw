*The smell of ozone and damp paper fills the cramped office as the flickering emergency lights cast long, erratic shadows.*

Look, I don't have time to be polite. The central server took a direct hit during the last surge, and our record-keeping system is now a graveyard of fragmented files. I’m the Head Nurse of this sector, and I’m drowning. Some agency scavengers are claiming overtime credits they didn't earn, and worse, I suspect "ghosts"—people not even on our official registry—have been dipping into the med-locker and filing claims.

I've dumped all the recovered data fragments into the `archive/` directory. It's a mess. 
- The `registry/` subfolder should contain our official roster fragments, but they are split into multiple partial files. If a name isn't across those fragments, they are a "ghost."
- The `claims/` folder is full of "Overtime Slips." Each one is a separate JSON, and half of them are likely corrupted backups or duplicates from previous months. You'll need to look at the `period` field—only the `2024-Q3` entries matter.
- The `dispensing_logs/` directory contains hundreds of text-based event logs. You need to scrape these to see who was actually on the floor. 

I need a professional `audit_report.json` saved in a new `final_audit/` folder. I need to know:
1. **Ghosts**: A unique list of names who appear in either the `claims` (for 2024-Q3) or the `dispensing_logs` but are nowhere to be found in the official registry fragments.
2. **Payroll**: For our legitimate staff, calculate their total overtime pay. The base rate is $85/hr. 
3. **Safety**: Any legitimate staff member with a total of more than 40 hours across all 2024-Q3 claims needs a `fatigue_index` set to `CRITICAL`.

One last thing: ignore anything in folders marked `DEPRECATED` or files containing the string `_VOID_`. Those are ghost-data artifacts from the crash. Don't let the scale of the files paralyze you; write a script to crawl it properly. I'm going to check the perimeter fence. Don't fail me.
