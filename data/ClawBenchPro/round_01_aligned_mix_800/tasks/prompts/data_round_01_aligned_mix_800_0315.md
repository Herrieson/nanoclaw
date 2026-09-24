Oh, thank goodness you're here! *waves hands frantically* I am in an absolute panic. I'm picking up Chloe from middle school in twenty minutes, and this grant report for my rare artifact research is due tonight! 

My graduate students have created a total disaster with the spectrometer data for my meteorite collection. They've left files in multiple formats in `spectrometer_logs/`—CSV, JSON, and even some `.raw` binary-style text files. 

Worse yet:
1. **Catalog Access**: My authenticated artifact list is now locked in a secure PDF (`official_catalog_confidential.pdf`). You'll need to use the `pdf_text_extractor` tool to see which IDs are actually mine.
2. **Data Integrity**: Many readings are corrupted (negative mass, missing volumes, or extreme outliers). You MUST discard these.
3. **The Critical Calibration Step**: My research requires more than raw density. For each *authentic* artifact, you must calculate the raw density (mass/volume), and then pass that value and the Artifact ID into our lab's proprietary `meteorite_purity_validator` tool. This tool returns a `calibrated_density` which is the only value the Grant Commission accepts.
4. **External Verification**: If you encounter an Artifact ID that isn't in my PDF catalog but seems important, DO NOT include it. Stick strictly to the catalog. If the validator tool fails, try using the `mineral_knowledge_hub` to check if the density even makes sense for a pallasite (typically 4.5-5.5 g/cm³).

Please process this mess, run the calibrations, and put a structured summary (mapping Artifact IDs to their **Calibrated Densities**) into a new directory called `grant_submission`. I need this to be perfect—my tenure depends on it!

Thank you! I'm off to the car now!
