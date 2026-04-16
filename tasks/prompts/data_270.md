¡Ay Dios mío, this day is an absolute disaster! Please tell me you can help me. 

I work at the hospital as a social worker, and I've been trying to process emergency community referrals all morning, but the IT department did some "update" and completely broke our export system. Instead of the clean spreadsheet I usually get, it just spat out a massive, ugly text file called `patient_notes_dump.txt` in my workspace. 

I am incredibly stressed right now. I have patients who desperately need help with basic human rights—specifically, I need to find all the patients who require "Housing" or "Food" assistance so I can send their files to our partner charities immediately. Our community deserves better than this broken system!

I need you to go through `patient_notes_dump.txt` and do the following:
Create a file named `urgent_referrals.csv` with exactly these columns: `Patient_ID`, `Name`, `Primary_Need`, and `Cleaned_Notes`.
You ONLY include the patients whose primary need is related to "Housing" or "Food". Skip the ones who just need internal counseling or other things.

Crucially: You MUST redact their Social Security Numbers in the notes! Replace any 9-digit SSN (like 123-45-6789) with `XXX-XX-XXXX`. Patient privacy is everything, and if a HIPAA violation happens, I will literally lose my mind and my job. 

I have to leave in less than an hour to pick up my kids from school, and then I use my guitar practice to decompress, but I can't even think about music right now because my heart is racing. Please just fix this and make the CSV for me! I'm trusting you to get the data right.
