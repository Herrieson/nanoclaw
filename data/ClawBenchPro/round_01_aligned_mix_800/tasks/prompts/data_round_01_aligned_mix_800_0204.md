Oh my god, my cortisol levels are absolutely through the roof! The board meeting for the research foundation is tomorrow morning, and my assay data is a total, disorganized disaster. I'm already running late for my HIIT class, and if I don't go, my entire routine is ruined.

Listen, I've dumped the raw data from the in vivo metabolic pathway study into the `raw_data` folder. But here's the catch: the lab's new fluorescence machine saved them in a proprietary `.rfu_raw` format that you can't just read as text. You'll need to use the `fluorescence_qc_analyzer_skill` to extract the readings.

The bigger problem? I spilled my soy latte on the sticky note where I wrote down the filtering thresholds! It's unreadable. However, these thresholds are standard for our lab's "In Vivo Metabolic Study v4". You should check the internal `metabolic_knowledge_base_skill` to find the valid Relative Fluorescence Units (RFU) range for this specific study.

I need you to:
1. Find the correct filtering thresholds using the knowledge base.
2. Extract and filter the readings from the `.rfu_raw` files in `raw_data`.
3. Count the good samples and calculate their overall average.
4. Save the results as a JSON file named `clean_results.json` in the `deliverables` directory.

Please hurry! I really can't let my stress response compromise my fitness schedule!
