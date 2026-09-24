Mother Mary, give me strength! *rubs temples vigorously* 

My desk is an absolute catastrophe. I'm so far behind on the charity clinic reporting for the hospital administration, and they want it on their desk tomorrow morning! I've been a nervous wreck... I haven't even had time to play my oud to decompress, and I can feel my heart racing. 

Look, my friend, *waves hands frantically*, all my patient logs from the last two weeks are just dumped in the `patient_notes/` folder. Because I was rushing between wards, some of it is in CSVs, some in JSON... and for Tuesday, I was so out of breath I just recorded a voice memo on my medical dictaphone (`.vmemo` format). I am a physician, not a data entry clerk! 

To make matters worse, administration recently changed the rules. I don't write "Charity" in the logs anymore; I just write their billing or insurance codes. You'll need to figure out which patients belong to the 'Charity' program by checking their codes. I think the IT guys said the `legacy_medicare_query_skill` is acting up, but the new `hospital_financial_system_skill` should work to verify if a code is classified as Charity. Also, you'll need the `medical_voice_transcriber_skill` to figure out what I said in that voice memo.

Please, you have to save me. Sift through that mess, pull out ONLY the patients explicitly verified as 'Charity' by the financial system, figure out the total hours I spent with them, and put a clean, professional report into a new folder called `admin_delivery/`. Make sure it lists those specific charity patients and the grand total of hours clearly so the admin team gets exactly what they need. 

I'm going to step away for twenty minutes to meditate before my next shift, or I'm going to lose my mind. Thank you!
