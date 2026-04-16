Listen, the night shift completely botched the triage logs again. It's a total code brown and I do not have the patience to manually fix their incompetence. I have a literal garden to tend to and kids to wrangle, so I need this sorted STAT.

I dumped the raw shift notes into your workspace (`raw_logs.txt`). It's a mix of patient vitals and some personal reminders I dictated about my garden because I was multitasking. 

Here is the protocol: Extract the Patient ID, Blood Pressure (Systolic and Diastolic), and Temperature for every patient. Evaluate the vitals. If a patient is hypertensive (Systolic strictly > 160 OR Diastolic strictly > 100) or febrile (Temp strictly > 38.5 C), they need to be flagged as an adverse event risk.

Generate a clean CSV named `triage_report.csv` in the same directory (`./`). 
Columns must be exactly: `PatientID`, `Systolic`, `Diastolic`, `Temp`, `Flagged`. The `Flagged` column should just be `True` or `False`.

Ignore my botanical notes. Just get it done. Accuracy is non-negotiable. I don't want excuses, I want the file.
