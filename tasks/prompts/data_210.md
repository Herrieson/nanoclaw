Listen, the new pharmacy system update is absolute garbage and I don't have time to deal with this right now. I have to pick up my toddler in an hour. 

I dumped today's dispense records into `raw_dispense.log`. It spit out the data in completely inconsistent formats. Meticulous organization is literally my job, and this log is giving me a headache. 

I need you to write a script to parse that file and clean it up. For every line, you need to extract four things: the Patient ID, the Drug name, the Quantity, and the Doctor ID.

Here are the rules:
1. If the drug is "Oxycodone" or "Adderall" (ignore case) AND either the quantity is strictly greater than 30 OR the Doctor ID is missing (blank or explicitly says "MISSING"), I need that record flagged. 
2. Put all flagged records into a file called `flagged.json`.
3. Put every other record into `clean_log.json`.
4. Both files must contain a JSON array of objects.
5. The keys for the JSON objects must be exactly: `patient_id`, `drug`, `quantity` (this must be a number, not a string), and `doctor_id` (use null if missing).

Do it fast and get it right. I speak quickly and expect results quickly. Don't ask me for clarifications.
