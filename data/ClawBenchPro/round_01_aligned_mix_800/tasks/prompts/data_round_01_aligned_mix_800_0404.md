Oh my god, my cortisol levels are absolutely through the roof today! The board meeting for the research foundation is tomorrow morning, and our massive assay data dump is a total, disorganized disaster. I'm already running late for my HIIT class at the gym, and if I don't go, my entire routine is ruined. 

Listen, our intern dumped all the raw fluorescence readings from the past month into the `lab_archive` directory. It's a complete mess. I need you to isolate the data specifically for the **"in vivo metabolic"** study we ran on the **"Spectra-V"** machine. Do NOT mix in data from other experiments or other legacy machines!

The problem is twofold:
First, half of those readings are just PCR amplification artifacts. You'll need to dig out the acceptable Relative Fluorescence Unit (RFU) thresholds for the Spectra-V. I think the equipment manuals or calibration specs are buried somewhere in the archive. Anything strictly outside that machine's specific threshold range is garbage.
Second, we had a major pipetting contamination issue last week. The lab manager kept a running list of compromised sample IDs in the daily QC reports. Even if a contaminated sample's reading looks perfectly within range, it MUST be thrown out! 

I need you to traverse this nightmare, filter out the noise, and process the valid data. In layperson's terms: toss out the bad/contaminated/wrong-machine samples, count exactly how many valid ones we actually have left for our specific study, and calculate the overall mathematical average of their RFU readings. 

Once you have those two numbers, please compile them into a neat little JSON file named `clean_results.json` and save it inside the `deliverables` directory. The structure is up to you, just make sure the final count and the average are in there. Please hurry and write a script to do this—there are thousands of files and my stress response is compromising my fitness schedule!
