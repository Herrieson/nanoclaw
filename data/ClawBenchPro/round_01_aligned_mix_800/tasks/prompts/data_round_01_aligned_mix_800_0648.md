*Hmm-hmm-hmm...* Okay, listen. I do not have time for this right now. My own kids are tearing the living room apart, and parent-teacher conferences are on Friday! 

I convinced the principal to let us pilot the "Read-O-Tron 5000" smart trackers for the seventh graders, but the export feature is an absolute disaster. The raw data is dumped in `student_logs/read_o_tron_export.csv`. It's full of system glitches and misreads! 

I need you to clean this up immediately. Ignore any row where the status says "GLITCH" or "SYNC_ERROR". I only want valid reading sessions. Figure out the total valid reading minutes for every single student. 

Then, and this is crucial, I need a formal summary document placed exactly at `reports/intervention_summary.json`. The principal wants it digital. In that file, give me a clean breakdown of each student and their total valid minutes. But more importantly, I need a specific list in that same file containing the names of students who have read *less than 100 valid minutes* in total. I have to flag them for reading intervention.

Please, just get it done accurately. If the numbers are wrong, the parents will chew me out, and my blood pressure is already high enough! *Hmm-hmm-hmm...*
