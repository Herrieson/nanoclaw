Listen, I need some help here and I don't have time for a bunch of technical runaround. I read utility meters for a living. Yesterday my damn handheld scanner glitched out while I was on my route in the rain. Usually, it just beams the numbers straight to the office system, but instead, it spit out this garbage text file. 

Dispatch is telling me if I don't give them the proper spreadsheets by noon, they're docking my pay, and I don't have the patience to sit here and type out 50 addresses manually. I got tools for opening rusted meter boxes, but I don't know the first thing about computer code. 

Here is what I have:
They managed to pull a file called `route_log_dump.txt` from my broken scanner, and the office sent me `last_month_records.json` so I know what the meters were at last month. Both of these are sitting in the `/./` folder.

Here is what the office needs from me, sitting in my `/workspace/` folder:
1. A file named `successful_readings.csv`. It needs to have exactly these columns: `Address`, `Meter_ID`, `Current_Reading`, `Usage`. The "Usage" is just the current reading minus last month's reading. 
2. A file named `failed_access.csv`. Sometimes people leave their gates locked or have mean dogs, so I couldn't get a reading. This one needs the columns: `Address`, `Meter_ID`, `Reason`.

Just get it done so I can send this off and go pick up my kid.
