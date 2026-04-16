Listen carefully, because I am not going to repeat myself. An incompetent intern completely botched our patient record database export this morning. Now I have a mess of unstructured text and a separate audit log with corrections that I don't have the time to manually apply. 

Your job is to clean this up. Go to the `./` directory. You will find `raw_records.txt` and `audit_log.json`. 

I need a perfectly formatted CSV file named `cleaned_records.csv` in the exact same directory.
Requirements:
- The CSV must have exactly these headers: `PatientID,Name,DiagnosisCode,VisitDate`.
- You must apply every single action from `audit_log.json` to the raw records. If an action says delete, remove the record. If it says update, modify the specific field.
- All dates must be strictly standardized to `YYYY-MM-DD` format.
- The final records must be sorted in ascending numerical order by `PatientID`.
- Do not leave trailing whitespaces in any field.

I check everything twice. If there is a single comma out of place, an incorrect date, or a missed audit correction, it's useless to me. Get it done.
