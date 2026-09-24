Look, I'm literally pulling my hair out right now and I don't have the patience for a long back-and-forth. The volunteer groups just sent in their trail inspection logs after the storm, and it is an absolute garbage dump of a CSV file. It's sitting right there in `raw_data/trail_logs_2023.csv`. 

My dad expects me to lead a trail clearing and camping expedition this weekend for the family business, but I can't even process this mess. Some of these volunteers don't even know how to write down a valid kilometer marker! 

You know I need to see things visually before I head out into the woods. I need you to parse that data and figure out which sections are critical hazards—anything with a severity of 8 or higher. Ignore the sections where the kilometer marker is garbled or missing, I can't guess where those are. 

Here is what I need you to do, and please, just get it done:
Create a new folder called `planning`. Inside it, make me an `action_plan.md`. I need a clean, highly readable visual table in there showing only these critical hazards. I also need you to figure out what gear I should pack for each issue based on the problem (e.g., if it's a fallen tree, obviously I need a chainsaw; if it's erosion or a mudslide, shovels). 

Also, I'm plugging this into my dad's GPS software later, so I need a strict JSON file in that same folder called `gps_pins.json`. Just map the critical Trail IDs directly to their kilometer markers so the software can ingest it. 

I'm incredibly stressed and just want to meditate instead of dealing with this, so please don't mess this up.
