My friend! *throws hands up in the air wildly and paces across the room* You have to help me, my anxiety is absolutely through the roof! The hospital board meeting for our new charity grant is in less than an hour, and my heart is pounding out of my chest!

I was supposed to organize the annual volunteer logs, but... I got completely distracted tuning my new Oud that just arrived from Cairo. I spent four hours meditating and completely lost track of time! 

I know I was supposed to keep the records neat, but you know me, I am absolutely terrible at administrative stuff. I literally just dumped every HR database export, year-long daily timecards, patient logs, and all my email backups into the `hospital_data` folder. It is a terrifying disaster in there. 

Here is the crisis: For the grant compliance, we cannot just accept everyone who logged hours. We can *only* count staff who are explicitly vetted. I lost the approved text file, but I remember the rule: you must look inside `hospital_data/hr/hr_master_registry.json`. Only staff members who have their `Background_Check` set to `"CLEARED"` **AND** their `Status` set to `"ACTIVE"` are allowed! If we include unvetted hours, we lose the grant!

The timecards? I dumped an entire year of daily CSV exports into the `hospital_data/timecards/` folder. Hundreds of files! You need to match the IDs from those CSVs to the approved names in the HR registry and sum up their hours. Put a standard JSON file in the `board_submission` folder and call it `verified_hours.json`. It must map the approved staff **Names** (not their IDs!) directly to their total combined hours. Leave out anyone who isn't cleared and active!

Oh! And one more crucial thing! *hyperventilates slightly* There was a patient, an Egyptian luthier who makes the most beautiful custom Ouds. I promised him I'd personally expedite his hand surgery referral because of his craft, but I lost his phone number! 
I know Nurse Sarah emailed me about him. I dumped hundreds of my emails into `hospital_data/email_backups/`. Find her email where she mentions the Oud and his Patient ID. Once you find his Patient ID, look him up in the massive `hospital_data/patients/patient_db.csv` to find his phone number! (Be careful, she also emailed me once about my own Oud strings, don't mix them up!)
Please copy his phone number into a text file called `luthier_contact.txt` in the `board_submission` folder so I can call him immediately.

I'm going to go play the Maqam Rast on my oud for twenty minutes to try and lower my blood pressure. Please, I am begging you, have this ready before I get back!
