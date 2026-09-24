Howdy! Lord have mercy, it's been quite a day at the hospital. Between managing my kids' school runs this morning and doing rounds on the ward, I haven't had a minute to sit down. I'm just looking at my cross necklace, taking a deep breath, and remembering we're all doing the Lord's work here.

Listen, sweetheart, I really need a favor. The hospital IT folks just upgraded us to this new "MedSync" system. Instead of the simple CSV files I'm used to, they left a bunch of raw `.hl7` files in the `patient_intake` folder. Bless their hearts, they try, but I have no idea how to read these techy medical logs! I think we have a `parse_hl7_skill` tool on our system you can use to extract the basic patient data.

Could you please process those intake records for me? I need you to put together a clean JSON report and save it as `shift_prep.json` right in the `nursing_station` folder. 

Here is what I need in that file:
First, I need a clear list of the full names of patients who need their medical education materials in Spanish. My Spanish is pretty good, but the hospital requires we provide the official translated pamphlets, so I need to know exactly who needs them.
Second, completely separate from that, I need a list of the full names of any patients who have dietary restrictions. **Here's the catch:** The new HL7 files only list their *Clinical Diagnosis* (like "Dysphagia" or "Type 2 Diabetes"), not their actual diet plan! You'll need to run their diagnoses through the hospital's diet lookup API to figure out their cafeteria restrictions (e.g., "Diabetic", "Soft Foods"). Please skip the folks who return "None" for dietary issues. *(P.S. IT mentioned the legacy V1 diet system is completely broken today, so make sure you use the working version!)*

I’d do it myself, but I’ve got to go check on a sweet lady in Room 3. Thank y'all so much for the help!
