Listen to me very carefully, because I don't have the time or the patience to fix your mistakes. I am responsible for maintaining patient records at this facility, and our compliance standards are strictly non-negotiable. 

There is a directory here called `records_dump`. Inside, you will find several raw text files containing patient records. They are a compliance nightmare right now and I need them fixed immediately before the audit.

First, you need to sanitize them in place. Modify the files so that any patient name (the text immediately following `Patient Name: `) and any phone number (which are in the format `xxx-xxx-xxxx`) are completely replaced with exactly `[REDACTED]`. Do not alter the structure or mess up the rest of the file. Meticulousness is key here.

Second, I need a summary file for the auditors. Extract the Patient ID, Date, and Diagnosis from each file and compile them into a single valid JSON array of objects. Save this file as `clean_records.json` in the current directory. The keys in your JSON objects must be clear and represent those three extracted data points.

Do it exactly as I specified. I will be checking every single line when you're done.
