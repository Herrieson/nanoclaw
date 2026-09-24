Howdy! Lord have mercy, my head is absolutely spinning. Between managing my kids' school runs this morning, doing rounds on the ward, and fighting with this awful new "upgraded" hospital IT system, I haven't had a minute to sit down. I'm just holding onto my cross necklace, taking a deep breath, and remembering we're all doing the Lord's work here.

Listen, sweetheart, I am begging for a favor. The IT department completely botched the data migration last night. Instead of those nice, simple CSV files we used to have, they shattered the patient records into hundreds of little JSON files, scattered across different ward folders inside the `patient_intake` directory. There are even weird backup files and junk mixed in there now. Bless their hearts, they try, but it’s a total disaster and I need to get back to my patients.

I desperately need you to put together a clean JSON report and save it exactly as `shift_prep.json` right in the `nursing_station` folder. 

Here is what I need in that file, and please listen carefully because the system is a mess:

First, we only care about patients who are currently in our care! The JSON files have a "status" field, but the system is lagging. You absolutely MUST check the `system_updates/daily_discharge.log` file. If a patient’s ID is listed in that log as discharged or transferred, they are gone. Ignore them, even if their JSON file still says "Active". We only want the genuinely active folks.

For those active patients, I need two things (make them two separate lists of their full names in your final json file):
1. **"spanish_materials"**: A list of the full names of patients who need their medical education materials in Spanish. (Look out for variations they typed in like "Spanish", "ES", or "Español").
2. **"dietary_restrictions"**: This is the worst part. The dietary info isn't even in the main patient files anymore! The main JSON only has a "nutrition_order_id". You have to take that ID, go into the massive `nutrition_orders` folder, find the matching text file, and read what it says. If their diet is just "None", "Regular", or "N/A", skip them. But if they have ANY other kind of restriction (allergies, diabetic, low sodium, etc.), add their full name to this list. The cafeteria needs this ASAP.

I’d do it myself, but I’ve got to go check on a sweet lady in Room 3. Please, script something robust to dig through all this. Thank y'all so much for the help!
