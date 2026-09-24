*tap, tap, tap* 

Dios mío, you hear that? That's my foot tapping because I've been waiting an hour for dispatch to answer the radio. I'm sitting in my cruiser, the AC is busted, and my Mobile Data Terminal looks like it was programmed by a racoon. 

Look, I'm supposed to be enforcing motor vehicle laws, not doing forensic IT work. They migrated to a new "decentralized" system last week, and now everything is a dump site inside the `dispatch` folder. I need you to comb through this mess for me, because I refuse to go blind looking at raw text.

Here's the headache:
First, they dumped all the stolen vehicle records into the `dispatch/active_cases/` folder. It's a complete maze of different precincts and file formats. I need you to figure out which plates are *actually* still stolen. Don't give me cars that have a status of "RECOVERED" or "CLOSED" – I only want the ones marked "STOLEN" or "WANTED". 

Second, the automated traffic cameras are vomiting raw logs into `dispatch/camera_logs/`. It's sorted by date, but I only care about **today's** data: **October 24th, 2023**. Read through today's logs and tell me two things:
1. Did any of those *currently* stolen plates pass by our cameras today?
2. Where is the absolute worst location for speeding today? I'm talking about the highest number of cars going *over 65 mph*. 

Oh, and a warning from the IT guy: the sensors spit out logs by their machine `SENSOR` ID (like CAM_01), so you'll have to find the system config file somewhere in `dispatch` to translate that into an actual street name. Also, if a camera log says the status is "TEST" or "MAINTENANCE", ignore it! The calibration guys run fake cars at 150 mph to test the flash, and it ruins our stats. Only count "NORMAL" readings.

Take your findings and put them in a clean JSON file called `daily_briefing.json` inside a `reports` folder. Give me a list of the spotted stolen plates under the key `stolen_spotted`, and the actual street name of that terrible speeding location under `worst_hotspot`. 

Hurry up, I need to know where to set up my speed trap before my shift ends!
