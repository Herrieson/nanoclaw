*Hmm-hmm-hmm...* Are you there?! Listen, I do NOT have time to hold your hand right now. My own kids are tearing the living room apart, and the parent-teacher conferences are on Friday! 

I convinced the principal to let us pilot the "Read-O-Tron 5000" smart trackers for the **7th Graders only**, but the IT department botched the deployment completely. The raw data isn't in one file; it's shattered into a million pieces somewhere in the `device_sync` directory. Half of those files are from last year's old 4000 model! I can't look at 4000 model data; it's irrelevant. 

Oh, and IT left the student rosters over in the `school_system` folder. You need to figure out who the 7th graders actually are. The logs only use those ridiculous student IDs! 

I need you to clean this up immediately. Find the manual IT left lying around—it tells you which status codes actually mean the kid read, and which ones are just system malfunctions. Oh, and a heads up, my colleague just texted me: *"The new 5000s log everything in SECONDS instead of minutes!"* Are you kidding me?! I need MINUTES. 

I need a formal summary document placed exactly at `reports/intervention_summary.json`. The principal wants it digital. In that file, give me a dictionary called `student_totals` mapping each 7th grader's **full name** (First Last) to their total valid reading **minutes**. Then, make a list called `intervention_list` in that same file containing the full names of 7th grade students who have read *less than 100 valid minutes* in total. 

Please, just get it done. Figure out the folders, match the IDs, convert the time, ignore the old devices, and give me accurate numbers. If you mess this up, the parents will chew me out, and my blood pressure is already sky-high! *Hmm-hmm-hmm...*
