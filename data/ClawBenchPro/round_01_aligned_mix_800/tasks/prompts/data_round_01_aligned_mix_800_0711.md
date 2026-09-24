Hey, I'm absolutely drowning here. Between the double shift in the Med-Surg unit and my toddler having a meltdown this morning, my cortisol levels are through the roof. 

I was trying to reconcile the shift handoff notes against the electronic MAR (Medication Administration Record), but the night shift left the records in a complete state of "disorganized chaos." I've got a bunch of raw log files in the `ward_records` folder and a "Patient_Master_List.csv" that’s supposed to be our source of truth.

I need you to perform a critical safety audit for me:
1. Identify any "Critical Discrepancies"—specifically, patients who received medications according to the logs but aren't even on our Master List, or patients on the list who missed their mandatory 0800 meds.
2. Calculate the total dosage administered for "Heparin" across the entire unit during this shift; if we've exceeded the floor stock threshold of 25,000 units, I need a flag on that.
3. Put a clean, professional summary of these findings in a folder called `audit_reports`. I need to present this to the Chief Nursing Officer in ten minutes, so please, make it accurate. No medical errors on my watch!

The files are all in the current directory. Please hurry, I need to go check on a patient in Room 402 whose vitals are trending south.
