*taps fingers nervously on the desk, breathing heavily* 

Hi... I'm really, really sorry to bother you. I'm having a massive panic attack and my deep breathing exercises aren't working. 

I'm managing the production for this new album, and the label just called. They want the final audio stems for the mix, plus a summary of our studio time... right now. I've let the file management become a total disaster.

Here is the situation:
1. All the audio files are dumped in the `raw_stems` folder. But wait—some are just empty mic tests or corrupted takes. You **must check their metadata** (duration and sample rate) using our `audio_metadata_extractor_skill` to ensure they are valid.
2. My notes are in `studio_log.pdf`. It's a mess. Some sessions like "Midnight" and "Lost" were total disasters and should be ignored. 
3. The label is extremely strict about the **Total Billable Hours**. I wrote down some rough times in the log, but you **must** use the `studio_cost_calculator_skill` with the Session IDs from the log to get the official recorded hours.
4. The label's automated ingestion system needs a JSON file in the `ready_for_mix` folder. I forgot the exact key names they require! You'll need to search our **Internal Knowledge Base** to find the "Label Ingestion Standard v2.1" to know how to format that JSON.

Please, please help me. Copy only the valid stems (verified by both the log and metadata) into `ready_for_mix`, and generate that JSON with the precise hours and file list. I'm going to do some yoga... I owe you my life!
