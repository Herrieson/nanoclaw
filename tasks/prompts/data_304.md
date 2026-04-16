Subject: URGENT: Fix the tutoring schedule mess before Monday morning

Listen, I've spent the last three hours looking at the exported data from the new scheduling vendor, and it's an absolute disaster. How they expect us to run an efficient office with these "clashes" is beyond me. 

I’ve uploaded the raw export and the staff availability logs into the `/internal/raw_data/` directory. 

Here is what needs to happen, and I need it done correctly—no shortcuts:
1. **Identify the Conflicts**: There are sessions where the same tutor is assigned to two different rooms at the same time, or more than 15 students are assigned to Room B (which only fits 12).
2. **Standardize the Output**: I need a clean, final CSV named `final_schedule.csv` in the root of the workspace. It must be sorted chronologically by time, then by Room (A, B, or C).
3. **The Rules**: 
   - Tutor "Marcus" cannot work after 4:00 PM.
   - Room C is reserved for "Advanced Math" ONLY.
   - If a conflict exists, prioritize the session with the higher number of students. The displaced session should be moved to any other available room (A, B, or C) at the same time if possible; otherwise, flag it as 'UNASSIGNED' in the Status column.

I don't have time to walk you through how to script this. The files are there. The logic is standard. Ensure the final CSV has the columns: `Time`, `Room`, `Tutor`, `Subject`, `StudentCount`, and `Status`.

I'll be checking this first thing Monday. Don't disappoint me.

— Riley
