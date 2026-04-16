Hey. Listen, I need this sorted fast. I'm hitting the road in an hour for my Chicago run. 

I bought this new open-source GPS tracker module off Kickstarter for my rig. Super cool hardware, but the software is on me. I tried to write a Python script to calculate my total mileage and figure out exactly where I stopped and for how long on my last route. I read up on some Haversine formula stuff on a tech blog and slapped it together, but my code is garbage and just throws errors. 

To make matters worse, the Bluetooth connection to the tracker dropped a few times, so the log file has some corrupted junk lines in it. I don't have time to clean it up manually. 

My workspace is in `./`. You'll find my log file `tracker_data.csv` and my broken script `process_gps.py` in there. 

Fix my script so it ignores the junk lines, correctly calculates the total distance in kilometers, and finds my stops (any continuous period where speed is 0). Have it output a `summary.json` in that same directory with `total_distance_km` (rounded to 2 decimal places) and a list of `stops` (each with `lat`, `lon`, and `duration_minutes` as an integer). Just get it working, I don't care how ugly the code is as long as the numbers are right.
