Oh, for heaven's sake... I am literally tapping my fingers on my desk so hard I might break a nail. My anxiety is absolutely through the roof. 

Listen, I need your help to fix this catastrophe, and I need it done perfectly. I'm the lead receptionist for the State Administration, and my desk—much like my life since the divorce—is currently a disaster zone. I spent weeks organizing the "Healthy Cooking & Balanced Lifestyle" seminar for our state employees. It's an issue I care deeply about (unlike my ex-husband who survived exclusively on canned chili, but I digress). 

The seminar was yesterday, and the temp workers completely botched the sign-in process. Instead of putting things in one neat spreadsheet, they dumped everything into the `events_raw/` directory, mixing our seminar logs with hundreds of old, useless files from past years' fire drills and holiday parties. Thankfully, I was smart enough to tell them to stamp the first line of our event's files with exactly `EVENT_CODE: HCBL-2023`. Also, every time someone signed in, the system at least recorded them with a strict format: `[SIGN_IN] ID: PA-xxxx | Name_Used: xxxx`.

And to make matters worse, our IT department—bless their completely incompetent hearts—managed to shatter our centralized state directory! It used to be one beautiful JSON file. Now? It’s broken into hundreds of fragmented files scattered deep inside the `HR_database/` directory.

I know for a fact that some people off the street snuck into my seminar just for the free quinoa bowls. Or worse, fired employees who think they still get state perks! 

I need you to dig through the wreckage. Cross-reference the valid sign-in logs from our seminar with the fragmented HR database. A valid state employee must have a record in the HR database and their status must strictly say `Active`. 

Once you figure out who is who:
1. Create a brand new folder called `audit_report`. 
2. Inside it, make me a beautifully organized `clean_attendance.csv` containing only the valid state employees who attended. I want the columns to be `ID`, `Employee_Name`, and `Department`. (Please use their real names from the HR database, not whatever fake nickname they scribbled at the door!)
3. Create a separate `unauthorized.txt` file listing the exact `Name_Used` and the ID used by those gatecrashers (people who aren't in the database at all, or whose status is not Active). Format the text file however you want, as long as it has both pieces of info.

Please be thorough. There are hundreds of files, so don't try to guess or read them manually. I pride myself on having zero errors when the auditors come around. Fix this for me!
