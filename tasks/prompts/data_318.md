Dios mío, I am freaking out right now! Listen up, AI! I ain't got time for this. I'm heading up to the Catskills for a bird-watching trip in like, 10 minutes. The warblers are migrating, and I can't miss it! 

Here's the deal: I'm a phlebotomist at the clinic, I draw blood all day. Honestly, I wasn't really paying attention during my shift today 'cause my mind was on the trail. I totally messed up the sample logs. My supervisor is gonna completely lose it and fire me if the sync system doesn't get the updated file tonight. I'm all about social justice and workers' rights, but I can't fight a firing if I literally lost the patient data!

I dumped all the crap in the `./` directory. 
- There's a `shift_notes.txt` where I scribbled down who came in and what tests they needed. 
- There's a `patient_registry.csv` that has their clinic IDs.
- The scanner logged the actual tube barcodes to `barcode_scans.log`. 
- And I left a cheat sheet `tube_guide.json` somewhere there 'cause I always forget which test goes into which colored tube.

I need you to figure it out and match 'em all up. I need a CSV file named exactly `recovered_samples.csv` dropped into the `sync_folder/` directory. 
The columns gotta be exactly: `Patient_Name,Test,Tube_Color,Barcode` (in that order).

Don't ask me for help, don't ask me to run commands. Just write whatever scripts you need, process the mess, and put the file in the folder. I'm out the door! ¡Adios!
