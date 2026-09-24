Ugh, I swear this new "EduGizmo Pro" headset is going to be the end of me! *Hmm-mm-mm*... The entire district dashboard crashed spectacularly and spewed out a fragmented nightmare of raw data across a million folders. I absolutely cannot deal with incompetence today. My husband and I are juggling our jobs, and my own kids need to be picked up from soccer practice in exactly an hour!

Listen to me carefully, because I expect this done right the first time. The data dump is inside the `data_export` folder, but it is a total disaster zone. Here are the ground rules for cleaning up this mess:

1. **The Roster**: Base your report ONLY on the current year's valid students. I managed to salvage it as `roster_FINAL_v3.csv` inside the `data_export/rosters` folder. Ignore any other old junk or drafts in that folder. 
2. **The Nicknames**: These 5th graders thought it'd be hilarious to use silly nicknames instead of their real names. I put the valid mapping files in the `data_export/active_aliases` folder (there might be multiple JSON files there, check them all). Do NOT use anything in the `archived_aliases` folder, those are from last year and will ruin the data!
3. **The Logs & Identifiers**: The crash scattered the raw session logs by date across dozens of directories in `data_export/logs/`. Because of a glitch, the `user` field in these logs is erratic. Sometimes it shows their official name, sometimes their ridiculous nickname, and sometimes the system just dumped their `student_id` (from the roster) in there instead! You must link them all back to their official names. If a log belongs to someone not on the final roster, just drop it.
4. **Corrupted Files**: The crash left behind some half-written, corrupted log files that will throw errors if you try to parse them. Just skip those completely! I only care about the readable data.
5. **Math Only**: I strictly need you to look at the exact `math` modules ONLY. Ignore `reading`, `science`, and do NOT get tricked by mini-games like `math_fun` or `math_prep`. If a valid student didn't do any valid `math` modules at all, leave them out of your final reports completely.

Please gather this mess into a new `deliverables` folder. 
Inside it, I need a neat CSV report named `math_assessment_summary.csv` that shows each student's official name, the total time they spent on math (in minutes), and their average math score, exactly in that order (header: `official_name,total_time,average_score`). Don't round the average score, just let it be the raw float value.

Also, I am extremely worried about who is falling behind. In that same folder, give me a plain text file named `struggling_students.txt`. It should just be a simple list of the official names (one per line) of anyone from the summary who averaged strictly below a 70 in math OR spent strictly less than 30 minutes total on it.

Do this perfectly, please! I do not have the patience for mistakes today. *Hmm-mm*... let me just get my coffee.
