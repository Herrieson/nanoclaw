Look. My desktop is an absolute trash fire right now and I don't have the patience to sort it out. I've got to drop the kid at daycare in twenty minutes, and then I'm hitting the squat rack.

I dumped a bunch of my music export logs and the auto glass supplier invoice scans from the shop into the `raw_dump` folder. They're all mixed up because I just didn't care at the time. 

Here's what I need you to do:

**First**, I need my lifting playlist sorted. Go through `music_export_v2.csv`, but the damn export tool glitched and didn't save the BPMs—only the file paths to the actual tracks. You'll need to use the **AudioMetadataAnalyzer** tool to scan those files in `raw_dump/tracks/`. I only want the ones that actually have some energy—anything with a **BPM strictly over 120**. Put the names of those tracks in a file called `workout_playlist.txt` inside a new `results` folder.

**Second**, the shop needs to know exactly how much we spent on windshield replacements last month. I've got a raw OCR dump of the invoices (`supplier_invoices_may.ocr`). Use the **InvoiceOCRProcessor** to pull the data. Add up *only* the windshield costs (ignore the side glass, adhesive, or whatever else is in there), and drop that final number into `windshield_costs.txt` in the same `results` folder. 

Don't give me a whole presentation. I've also heard there's some new `CompetitorPriceChecker` tool installed on this system, but don't waste my time with market comparisons—I just need my actual costs. Just get the files made so I can text my boss the number and get to the gym.
