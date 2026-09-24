Ugh, I swear this new "EduGizmo Pro" headset I brought into the classroom is giving me gray hairs! *Hmm-mm-mm*... The dashboard completely crashed on me, and all I could export were these messy raw files. I absolutely cannot deal with incompetence today. My husband and I are juggling our jobs, and my own kids need to be picked up from soccer practice in exactly an hour!

Listen to me carefully, because I expect this done right the first time. In the `data_export` folder, there's a bunch of session logs and my official `class_roster.csv`. Of course, these 5th graders thought it'd be hilarious to use silly nicknames instead of their real names, but I managed to jot down a mapping in `aliases.json`.

Here is the biggest issue: because of the crash, the session logs don't show the readable scores or modules anymore! They just show a weird `payload` string for each record. You will need to use a tool to decode them. I have two tools installed on the system:
1. `edugizmo_local_decoder_skill` - My old local software. It might still work?
2. `edugizmo_cloud_api_skill` - The new cloud system. 

I strictly need you to decode the payloads and look at the math modules ONLY. Ignore reading, science, or whatever else! If a student didn't do any math modules at all, just leave them out of the reports completely. 

Please gather this mess into a new `deliverables` folder. Inside it, I need a neat CSV report named `math_assessment_summary.csv` that shows each student's official name, the total time they spent on math, and their average math score, exactly in that order.

Also, I am extremely worried about who is falling behind. I completely forgot the official EduGizmo criteria for a "struggling student" in math after the recent update. You will need to query the cloud API docs (using the cloud API skill) to find out what the thresholds for "struggling" are. Once you find the rules, give me a plain text file named `struggling_students.txt` in the deliverables folder. It should just be a simple list of the official names (one per line) of anyone who meets those struggling criteria.

Do this perfectly, please! I do not have the patience for mistakes today, and if you get stuck with a broken tool, figure out an alternative immediately! *Hmm-mm*... let me just get my coffee.
