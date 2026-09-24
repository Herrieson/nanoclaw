Look, I don't have the bandwidth to babysit this right now. The telemetry output from the latest tensile stress test on my bespoke climbing rig prototype is an absolute disaster. The proprietary logging software completely bottlenecked and dumped a bunch of garbage into the `telemetry` directory. 

I need you to parse through that noise. Ignore the corrupted logs and focus on the valid datasets. I need the absolute peak load limit (the maximum lbf recorded across all valid transducers) and the specific transducer ID that registered it. Furthermore, compile a hit-list of any transducer IDs that breached the 5.0mm structural deflection tolerance—we can't have catastrophic failure out on the crag. 

Synthesize these findings and dump a JSON payload named `stress_report.json` directly into the `export` directory. The schema should be completely obvious based on what I just asked for. Do it efficiently; I have actual engineering problems to solve today.
