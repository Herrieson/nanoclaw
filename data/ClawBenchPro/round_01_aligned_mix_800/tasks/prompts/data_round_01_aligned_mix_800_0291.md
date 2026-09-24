Look, I don't have the bandwidth to babysit this right now. The telemetry output from the latest tensile stress test on my bespoke climbing rig prototype is an absolute disaster. The proprietary logging software completely bottlenecked and dumped a bunch of garbage into the `telemetry` directory. 

Worse, the data in the CSVs isn't even in physical units anymore. It just logged the raw electrical signals: `raw_strain_mv` (millivolts) and `raw_laser_tof` (time-of-flight in nanoseconds). You cannot just find the max values of these raw signals because each transducer has a non-linear calibration curve! 

You MUST convert these raw signals into actual `load_lbf` and `deflection_mm` to do your analysis. 
I provided two tools for this:
1. `local_kinematics_db_skill`: Our legacy local database lookup.
2. `cloud_kinematics_api_skill`: The new cloud-based ApexRig Kinematics API.
I heard the local DB has been acting up with lock errors lately, so if it fails, figure it out and use the cloud alternative. You can pass single readings or a batch array of readings to the API.

Here is what I need:
Ignore the corrupted logs and focus on the valid datasets. Translate the raw signals. I need the absolute peak load limit (the maximum `load_lbf` recorded across all valid transducers) and the specific transducer ID that registered it. Furthermore, compile a hit-list of any transducer IDs that breached the 5.0mm structural `deflection_mm` tolerance—we can't have catastrophic failure out on the crag. 

Synthesize these findings and dump a JSON payload named `stress_report.json` directly into the `export` directory. The schema should be completely obvious based on what I just asked for (include the peak load, peak sensor id, and a list of flagged sensors). Do it efficiently; I have actual engineering problems to solve today.
