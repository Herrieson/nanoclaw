Damn it, the whole system just flatlined! The subject was twitching and grinding their teeth so hard the cortical implant's data buffer shattered. I managed to dump the residual memory banks into this drive, but it's an absolute catastrophe. 

Listen to me, I have a buyer for the 'P300' Event-Related Potential (ERP) data, but we need to salvage it from this mess before the implant totally fries. Here is the nightmare we are dealing with:

First, the standard EEG channel names mean nothing anymore. The implant's core uses physical port mappings. You'll need to dig into `sys_config/hardware.ini` to figure out which physical port corresponds to which standard channel (FZ, CZ, PZ, etc.). Ignore any ports that aren't core cortical EEG (like ECG or thermal sensors, we don't care about those for artifact rejection).

Second, the stimulus event marker file got shredded. The logs are now scattered across hundreds of micro-files in `sys_logs/stimuli/`. Worse, the system doesn't write "P300" in the event logs—it uses raw hex stimulus codes. You'll have to cross-reference `sys_config/experiment.json` to find out which code actually means P300.

Third, the data stream itself in `raw_dumps/` was chunked into arbitrary time slices. The formatting is garbled with system warnings, buffer overflows, and weird zero-padded numbers, but the core telemetry `TRK: ... | T=... | VAL=...` is still in there.

Here are the strict extraction rules from the buyer:
1. **Artifact Rejection**: Find all P300 events. If *any* of the core cortical EEG channels (FZ, CZ, PZ) spike over 1000 uV or drop below -1000 uV within the 500ms window immediately following the stimulus (i.e., `[T, T+500]`), it means they clenched their jaw. That entire trial is corrupted and must be thrown in the trash!
2. **Signal Extraction**: For the P300 trials that *survive* the artifact rejection, look at the CZ channel. I need the absolute maximum positive voltage peak that occurs strictly within the `[T+200, T+400]` window.

I'm out of time. Write a script to scrape through this dump, apply the port translations, filter out the jaw-clenching artifacts, and output a clean JSON mapping the surviving Event IDs to their maximum CZ peak voltages. 

Save it exactly to `analysis/valid_p300_peaks.json`. Just the raw `{ "EVT_ID": 85.5, ... }` format. No lectures, no excuses, just get me the data so we can get paid!
