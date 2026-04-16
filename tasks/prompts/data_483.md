---
I don't have time to explain things twice, so pay attention. 

During the Q3 internal audit, I discovered that the automated migration script handled by the previous IT contractor was a total disaster. The patient export files in `raw_exports/` are corrupted. Specifically, the data columns for 'Diagnosis_Code' and 'Patient_SSN' have shifted in 30% of the records, and the 'Treatment_Notes' for high-priority patients are stuck in some useless Base64 encoding.

This is a massive HIPAA compliance risk. I need this fixed immediately before the Chief Medical Officer's review tomorrow morning.

Here is what you need to do:
1. Locate all `.csv` and `.log` files in the source directory.
2. Identify which records have mismatched columns (you'll know it's a mismatch if the 'Blood_Type' column contains numeric data or the 'SSN' column doesn't match the 3-2-4 digit format).
3. Decrypt/Decode the 'Treatment_Notes' column for any record where the 'Status' is marked as 'ENCRYPTED'.
4. Reconstruct a clean, unified master dataset named `final_patient_records_2023.csv` in the `sanitized/` directory. 
5. The final file must be sorted by Patient_ID (Ascending) and must NOT contain any of the temporary encoding markers.
6. Generate a summary report `audit_summary.json` detailing how many corrupted records were repaired.

Everything must be precise. I do not tolerate "approximate" work. If the SSN format is wrong or a single diagnosis code is missing, the entire task is a failure. Get to work.
