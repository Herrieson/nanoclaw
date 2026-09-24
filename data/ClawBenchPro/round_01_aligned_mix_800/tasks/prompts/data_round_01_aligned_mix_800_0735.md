Hey there! Chuck here. Listen, I'm hoping you can help a guy out with a bit of a data mess. 

I've been driving rigs across the Midwest for years, but I recently got really into IoT and smart gadgets. I rigged up this wild beta tracking system in my cab—hooked an ESP32 right into the OBD2 port, wired up a smart dashcam, the works! The idea was to automate all my expense reporting and route optimization so I'd have more time to read up on the new tech blogs instead of doing paperwork. 

But, well, I’m not exactly the most organized guy. I kinda just let all the gadgets dump their logs into a single directory called `logs_dump` on my laptop over the past week, and now it's a total disaster. 

My tax software needs my total fuel expenses for the week, and I need to know my total mileage from the electronic logbook. The problem is, I was flashing a custom ROM on the tracker mid-week, so some of the JSON files in the logbook folder are probably missing data or using different formats. Oh, and the fuel receipts CSV has some weird formatting because I scanned them with a buggy OCR app. 

Also, I'm trying to figure out which city I spent the most time idling in so I can tweak my routes. The dashcam spits out a raw text file with arrival and departure timestamps. I need to know which city had the longest single stop.

Could you do me a huge favor and crunch this data for me? I'm trying to feed the results into a custom home assistant dashboard I'm building, so I need you to create a brand new folder called `dashboard_api` and put a clean, organized JSON file in there containing the total fuel spend, the total miles driven, and the name of the city with the longest idle time. I don't care what you name the file or the specific keys, as long as it's standard JSON and has those three pieces of information clearly laid out! 

Thanks a million! Let me know when it's ready!
