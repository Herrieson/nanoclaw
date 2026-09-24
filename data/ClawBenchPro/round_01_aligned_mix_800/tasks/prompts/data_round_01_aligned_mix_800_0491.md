The prototype rig snapped during the final pull. The logging node went into a death spiral, scattering the telemetry data across the local flash storage like shrapnel. I've dumped the entire `raw_recovery` archive for you. 

I need the post-mortem report yesterday. Don't waste my time with the "ghost" files—the logger was spitting out empty buffers and deprecated legacy formats during the crash. You need to identify the valid sensor clusters from the `cluster_manifest.json` scattered somewhere in the wreckage to know which transducer IDs actually belonged to the active rig.

Find the absolute maximum load (in lbf) recorded during the failure event and the Transducer ID that felt the hit. I also need an array of all unique Transducer IDs that exceeded our 5.0mm deflection tolerance. 

The kicker? The data is fractured. Some sensors logged to CSV, others to individual JSON snippets. You'll need to piece them together. Save the final summary as `stress_report.json` in the `export` directory. The JSON should include `peak_load_lbf`, `peak_transducer_id`, and `breach_transducer_ids`.

And one more thing—check the `system_logs`. The rig had a "Sensor-B" failure halfway through. Any data points from sensors explicitly flagged as 'MALFUNCTION' in the log timestamps should be discarded, even if they show high values. I don't trust junk data.
