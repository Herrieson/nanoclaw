Look, I drive a rig all day for a living, but I love messing with new tech. I hooked up a custom Raspberry Pi OBD and GPS logger in my truck to track my routes. Great piece of kit, but my file management is absolute crap. I just dumped all the logs from last week into `truck_logs`. It's a complete mess—some are CSVs, some are JSONs, some are just weird text files, and they're scattered in different folders.

I need you to dig through that folder, pull out my speed and location data, and figure out two things for me:
1. My absolute top speed in mph.
2. The total miles I drove. (You'll need to figure out the distance between the consecutive GPS points in chronological order across all those valid files. Use the Haversine formula and use 3958.8 miles for the Earth's radius so we get the exact same math).

I don't care how you write the code or pull the data, just get it done. Save the final answer in a file called `summary.json` with exactly two keys: `top_speed` (a number) and `total_miles` (a number). Let me know when it's ready so I can pull it up on my tablet.
