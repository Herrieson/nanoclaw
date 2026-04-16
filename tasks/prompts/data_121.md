Listen, I don't have time to hold your hand through this. The legacy structural simulation tool we use for the new truss design spit out an absolute mess of telemetry logs, and I need the anomaly data isolated immediately for a load-bearing review. 

The logs are dumped in `/workspace/sim_logs/`. The system encapsulates the nodal sensor readouts in B64-encoded JSON payloads tagged as `RAW_PAYLOAD`. I need you to parse the logs, decode those payloads, and isolate any telemetry node where the `stress_level` strictly exceeds the nominal threshold of `85.0`. 

Output the findings to a CSV file named `anomalies_report.csv` in the `/workspace/./` directory. The CSV must have exactly these headers: `timestamp,sensor_id,stress_level,deflection`. Sort the rows chronologically by timestamp.

I expect high precision. Don't give me pleasantries, don't ask for clarification, just write the extraction script, execute it, and generate the report. Get to work.
