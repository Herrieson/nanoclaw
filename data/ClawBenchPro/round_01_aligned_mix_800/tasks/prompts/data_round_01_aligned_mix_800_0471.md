Hi there, it's Sarah from the Middle School Admin Office. I am absolutely losing my mind right now. We have the big 8th-grade Washington D.C. trip coming up, and our new district IT system just catastrophically crashed. 

Instead of my neat dashboard, IT managed to recover some fragmented files and just dumped them all into a directory called `school_system_dump`. It's a total disaster area. There are old backups, files from the wrong years, and data for other field trips mixed in. I love a good puzzle, but the school board needs the final numbers by tomorrow morning, and I'm hyperventilating.

Here is what I need you to figure out from that dump:
First, I need to identify the "interlopers." Some kids (or parents) submitted forms for the D.C. trip, but they aren't even allowed to go! You have to check their forms against the official rosters. The catch? The rosters are scattered JSON files in the `rosters` folders. You can ONLY trust roster files where the metadata explicitly states it is for `"academic_year": "2023-2024"` and `"grade": 8`. Anything else is old garbage or the wrong grade.

Second, the form submissions are scattered across dozens of CSVs in the `submissions` folder. You only care about submissions where the event code is EXACTLY `DC_8TH`. But beware, IT said there might be corrupted `.tmp` or `.bak` files in there—just ignore those and only read the actual CSVs.

For the budget, I need to know the total "Emergency Fund" collected. The fund is an extra 10% fee applied ONLY to valid, roster-approved students who have a `"Paid"` status on their `DC_8TH` form AND opted for `"Premium"` insurance. The tricky part is that the 10% is calculated based on their specific package's base fee, which you'll have to look up in `policies/pricing.json`. 

Could you please dig through `school_system_dump` and create a new folder named `final_audit` with exactly these two files?
1. `interlopers.txt`: A plain text file with a clear list of the unique full names (one per line) of students who submitted a `DC_8TH` form but are NOT on the valid 2023-2024 8th-grade rosters.
2. `summary.json`: A JSON file containing exactly two keys: 
   - `"valid_confirmed_students"`: The total number of valid 8th graders on the roster who submitted a `DC_8TH` form and have a `"Paid"` status.
   - `"total_emergency_fund"`: The exact total amount of the Emergency Fund collected.

I'm usually very patient, but this is a nightmare. Please, you're my only hope!
