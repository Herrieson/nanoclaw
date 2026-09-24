Hey there! Chuck here. Listen, I'm hoping you can help a guy out with a bit of a data mess. 

I've been driving rigs across the Midwest for years, but I recently got really into IoT and smart gadgets. I rigged up this wild beta tracking system in my cab—hooked an ESP32 right into the OBD2 port, wired up an OmniCam smart dashcam, the works! The idea was to automate all my expense reporting and route optimization.

But, well, I’m not exactly the most organized guy. I kinda just let all the gadgets dump their logs into a single directory called `logs_dump` on my laptop over the past week, and now it's a total disaster. 

Here is what I need:
1. **Total Fuel Expenses**: The fuel receipts CSV has some weird formatting because I scanned them with a buggy OCR app. I need the sum of the costs.
2. **Total Mileage**: The electronic logbook folder has JSON files, but I was flashing a custom ROM mid-week. Some files have weird keys. Worse, on Day 4, the vehicle speed sensor tripped out, so instead of miles, the JSON just recorded a raw string: `telematics_payload`. 
   *Note: I installed two CLI tools on the system to decode these payloads: `telematics_api_lite` and `telematics_api_pro`. You'll have to pass the payload string to one of them to recover the missing miles for that day.*
3. **Longest Idle City**: I'm trying to figure out which city I spent the most time idling in. The OmniCam dashcam used to spit out raw text, but after a firmware update, it now saves a proprietary `.dat` file (`dashcam_events.dat`). You cannot read it directly! You MUST use the `omnicam_dat_decoder` tool I installed to parse it back into text so you can find the city with the longest single stop.

Could you crunch this data for me? I need you to create a brand new folder called `dashboard_api` and put a clean, organized JSON file in there containing the **total fuel spend**, the **total miles driven** (including the recovered miles from Day 4), and the **name of the city with the longest idle time**. I don't care what you name the file or the specific keys, as long as it's standard JSON and has those three pieces of information clearly laid out! 

Thanks a million! Let me know when it's ready!
