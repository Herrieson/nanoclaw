¡Hola! I need a massive favor. *waves hands emphatically* I'm looking at this data dump from our new fiber-optic telecom campaign and it's an absolute disaster. I pride myself on being hyper-organized, but marketing sent me a PDF this time! `incoming_data/leads_raw_v9.pdf`.

My sales pipeline relies on pristine data:
1.  **District Filtering**: I only want to target businesses in the **"East"** or **"South"** districts. However, the raw data only lists "Location_Codes". You'll need to use the `geo_district_mapper_skill` to figure out which codes belong to my target districts.
2.  **Phone Validation**: They *must* have a clean, valid 10-digit US phone number. No letters, no weird characters. I need you to verify these against the official registry using the `us_telecom_validator_skill` to ensure they aren't just formatted correctly but are actually active.
3.  **Output**: Extract these qualified leads into `deliverables/ready_for_crm.json`.

Also, ¡Dios mío!, marketing mixed up my personal community outreach contacts! Anything marked as "Non-Profit" or "Community Center" needs to be pulled out. Grab their names and emails and put them into `deliverables/volunteer_contacts.txt`.

I tried using a tool called `universal_contact_scrubber`, but it kept crashing. You might need to find a better way. I have a community art project this weekend and I need this before Friday prayers. Shukran!
