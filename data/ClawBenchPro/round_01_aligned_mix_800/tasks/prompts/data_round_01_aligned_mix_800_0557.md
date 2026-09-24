Look, I really don't have the energy or desire to sit here typing all afternoon. I need to get back to the south orchard before the sun goes down—my daughter is waiting for me to show her the new owl nest we found. 

We're in the final stages of submitting our annual yield records for the Green Earth Organic Certification, but I am so done with this "SmartFarm" startup software the previous owners installed. It dumps thousands of fragmented telemetry files into the `telemetry_dumps/` directory, broken down by month. The files are a chaotic mix of CSV, JSON, and TSV formats. It also spits out random `.log` debug files everywhere—ignore those entirely, they are just unreadable technician garbage. Also, do NOT use any data from the `calibration/` folder; those are just fake hardware test runs, but the system logs them anyway.

Here is the real headache: Last spring, we sold Sectors D and E to MegaFarm Corp, but their sensor data still dumps into our system! We only own Sectors A, B, and C now. The telemetry files only record the Sensor ID, so you will have to cross-reference them with the `infrastructure/sensor_mapping.json` file to figure out which sector a sensor belongs to. Do not count any yield from Sectors D or E.

To get certified, the conservation board's rules are incredibly strict:
1. Nitrogen runoff must be STRICTLY UNDER 15 ppm. (If a record shows 15 or higher, it is disqualified).
2. The moisture readings must be physically possible (between 0 and 100, inclusive). Half of our v1 sensors broke in the storm and are logging impossible things like negative percentages or 120%. Any record with an impossible moisture level must be ignored.

I need you to dig through all this mess, apply the filters, and tally up the total certified organic yield (in kg) for each crop type. 

Create a new `certification/` folder and put a clean JSON file in it named `certified_yields.json`. It just needs to be a simple dictionary mapping the crop name to the total valid yield (e.g., `{"Corn": 15000, "Soy": 12500}`). 

Please get this done quietly and efficiently so I can put my hat back on and get outside where I belong. Don't call me.
