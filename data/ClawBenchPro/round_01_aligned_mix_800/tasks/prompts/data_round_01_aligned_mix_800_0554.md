Good morning. I’m sitting here at the front desk tapping my fingers to the bone, staring at this absolute digital nightmare. I've been with the State government's Human Resource Programs for twenty years. We used to have a perfectly orderly, structured sign-in book. Now, the higher-ups have installed this "modern" digital kiosk system across the lobby, and frankly, I despise it. It's disorganized, chaotic, and it’s raising my blood pressure—which is completely throwing off my healthy lifestyle balance!

Here is what you need to fix while I go take twenty minutes to meditate and reset my nerves:

First, they didn't even keep the department names in the logs! Everything is now masked behind cryptic "Department Codes". I hear the IT guys left a mapping file somewhere in the `config/` directory. You need to figure out the **Active** code for "HR Programs" and completely ignore anyone who isn't meant for my department.

Second, the lobby has 5 terminals (T01 through T05), and their logs are completely shattered across different files and formats inside `kiosk_data/terminals/`. To make matters worse, some idiot spilled coffee on Terminal T04 last week. It's currently in "MAINTENANCE" mode and is just spewing out corrupt test data and garbage logs. **Do not** process any data from terminals that are not actively running (there is a status file in `config/` that tracks this).

Third, the time formats in these files are a complete joke. Some use long strings of numbers, some use AM/PM, some use military time. I absolutely rely on structure. I need you to extract the valid HR Programs data and organize it into a clean, proper spreadsheet named `daily_appointments.csv` inside a newly created `processed` folder. This CSV must have three columns: `Time`, `Name`, `Reason`. 
*CRITICAL:* The `Time` column must be perfectly unified into the `YYYY-MM-DD HH:MM:SS` format, and the entire file must be **strictly ordered chronologically** from earliest to latest. 

Finally, maintaining proper health coverage is very important to me personally. A lot of people are coming in stressed out about their benefits. I left a memo on my desk (also somewhere in `config/`) that lists all the specific sensitive keywords related to insurance escalations. Please extract those specific individuals (from the valid HR list you just made) whose reasons contain ANY of those keywords, and put them into a separate text file called `insurance_complaints.txt`, also in that `processed` folder. The format should just be `Name: Reason` for each line.

I don't need to know the technical details of how you write your code. Just dig through the mess, cross-reference the configurations, and make it perfectly neat and accurate before I get back from my break. Thank you.
