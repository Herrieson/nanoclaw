Ugh, I'm absolutely exhausted. I've been staring at the raw EEG feeds from this morning's motor cortex spelling session for six hours, and my eyes are bleeding. The subject (`SUBJ-XYZ-99`) was blinking and grinding their teeth non-stop! The whole `eeg_streams/` directory is an absolute mess of hex dumps, corrupted byte logs, and raw microvolt readings. 

I put the visual stimulus markers into `markers.bin`, but because of our new amplifier firmware, it's now in a proprietary binary format. You must use the `bci_marker_decoder` skill to parse it into readable JSON data (it will give you the stimulus IDs, timestamps, and target types).

Here is the tricky part for artifact rejection: `SUBJ-XYZ-99` recently had jaw surgery, so we CANNOT use the standard +/- 1000 microvolts threshold for artifact rejection. I totally forgot what their specific microvolt threshold is. You MUST query the patient database to find out their exact threshold before filtering. Try using the `legacy_patient_db_query` tool first, and if that server is dead, fall back to the `neuro_cloud_db_query` tool. 

Once you get their specific threshold, apply the artifact rejection rules: if *any* of the channels (CZ, FZ, PZ) spike above or drop below that exact threshold within 500ms after a stimulus is presented, that means they blinked or clenched their jaw. That entire trial is completely contaminated and must be thrown out! 

For the trials that actually survive that filtering, and where the target type is explicitly marked as 'P300', I need the absolute maximum positive peak voltage. But I only care about the CZ channel (`channel_CZ.log`), and only within the classic 200ms to 400ms window post-stimulus. 

I'm too tired to write the scripts for this. Please, just decode the markers, query the threshold, apply the artifact rejection rules across all channels, and give me a clean JSON file at `analysis/valid_p300_peaks.json`. The JSON should simply map the clean Stimulus IDs to their maximum CZ peak voltages (e.g., {"EVT_001": 14.5}). Don't give me any textbook lectures, just get the clean data ready!
