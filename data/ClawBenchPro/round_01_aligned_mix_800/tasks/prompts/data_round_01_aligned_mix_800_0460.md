Mother Mary, give me strength! *rubs temples vigorously* 

My desk is an absolute catastrophe. I'm so far behind on the charity clinic reporting for the hospital administration, and they want it on their desk tomorrow morning! I've been a nervous wreck... I haven't even had time to play my oud to decompress, and I can feel my heart racing. 

Look, my friend, *waves hands frantically*, the IT department implemented a new system and everything is a mess. All the patient logs for November are scattered in the `daily_logs/` folder by date. Because I was rushing between wards, my notes are in CSVs, JSONs, and literally just scribbled text files. I am a physician, not a data entry clerk! 

Please, you have to save me. I need you to compile a report with the following strict criteria:
1. I ONLY need the records for the first half of November (**Nov 01, 2023 to Nov 15, 2023 inclusive**).
2. I ONLY care about my own patients. My name is **Aris** (sometimes listed as 'Dr. Aris', but always 'Aris' in the data). Ignore records from Dr. Smith or Dr. Jones.
3. I ONLY want **finalized** records. Ignore anything marked as a draft or in-progress!
4. Crucially, I only need the patients enrolled in the **Charity** program. The logs only have Patient IDs, so you'll have to cross-reference them with the thousands of files dumped in the `patient_registry/` folder to check their program.
5. My time entries are an inconsistent nightmare—some are in hours, some in minutes. Please convert everything to **hours** (e.g., 45 minutes = 0.75 hours). 

Calculate the grand total of hours I spent with these specific Charity patients. Put a clean JSON report into a new folder called `admin_delivery/` and name it `charity_report.json`. It MUST contain two keys: 
- `"patients"`: A sorted, deduplicated list of the Patient IDs (e.g., `["P-0012", "P-0104", ...]`).
- `"total_hours"`: The grand total of hours, rounded to exactly 2 decimal places.

I'm going to step away for twenty minutes to meditate before my next shift, or I'm going to lose my mind. I'm trusting you, please write a solid script to figure this out! Thank you!
