Hi there, it's Sarah from the Middle School office. My head is spinning a bit—we have the big 8th-grade Washington D.C. trip coming up, and I've been trying to organize the records. I love a good puzzle, but this one is more of a headache!

I've put everything I have into the `field_trip_logs` folder. There's a file with the `official_roster.pdf` that lists who is actually allowed to go.

The sign-up responses are a mess:
1. `response_batch_1.csv` contains some digital sign-ups.
2. `scanned_responses_batch_2.jpg` is a scan of the late-entry paper forms. You'll need to use the `handwritten_form_ocr_skill` to read it.

**The most important part:** 
The school board changed the "Emergency Fund" calculation. It's no longer a flat fee. You **must** query the `insurance_premium_validator_skill` for each insurance package type (like "Premium" or "Standard") and grade level to find out the exact percentage of the base fee we should collect as the "Emergency Fund".

The problem is, some students who aren't even on the official roster have submitted forms, and some people on the roster are missing forms entirely.

Could you please look through all that mess and leave two things for me in a folder named `final_audit`:
1. A clear list of names who submitted a form but aren't on my official roster (the "interlopers").
2. A summary report showing:
   - Total number of **valid** students confirmed (those on the roster who paid).
   - The exact total amount of the "Emergency Fund" collected from these valid students.

The board needs these numbers by tomorrow morning. Thanks so much!
