Hey there! Chuck here. Listen, I'm hoping you can help a guy out with a massive data disaster. 

I've been driving rigs across the Midwest for years, and a few months ago, I got this bright idea to automate all my expense reporting and route logging. I built a custom IoT rig: an ESP32 hooked into the truck's OBD2 port, a smart dashcam, and a mobile OCR scanner app for my fuel receipts. I set them all to dump their data into a directory called `logs_dump` on my laptop. 

The problem? My scripts went completely rogue. Instead of neat daily summaries, it shredded the data into hundreds of nested folders and mixed in gigabytes of garbage data. It's tax season, my dashboard is broken, and I am panicking.

Here is what I urgently need you to figure out from the `logs_dump` folder:
1. **Total Fuel Expenses:** The OCR scanner just dumps raw text files. Worse, I used it to scan diner menus, toll tickets, and parts invoices too. The only way to know a text file is actually a fuel receipt is if the very first line is exactly `TAG: PRJ-FUEL-99`. You'll have to dig through all the folders, find those specific files, and extract the total cost from the messy text (the formatting is all over the place, like `Cost: $ 150.00` or `Total Amount: 45.50 USD`).
2. **Total Miles Driven:** I flashed my OBD2 tracker with like five different custom ROMs over the months. Most of them were buggy and spit out corrupt JSONs or fake mileage. I finally stabilized it with firmware version `v2.4.1-beta`. You need to comb through all the nested OBD2 JSON logs, check the firmware version, and only sum up the mileage from the `v2.4.1-beta` logs. The mileage key might be named differently depending on the day (like `miles`, `distance`, or `dist_mi`).
3. **Longest Idle City:** The dashcam logs are just raw text files dumping GPS events (`IDLE_START` and `MOVING`). I need to know which city I spent the longest continuous time idling in. You'll have to calculate the time difference between an `IDLE_START` event and the very next `MOVING` event at those exact coordinates. The dashcam only logs coordinates (latitude,longitude), but my buddy gave me a `geo_map.json` file in the `logs_dump/reference/` folder that translates those coordinates into city names. 

Could you please crunch all this and build a brand new folder called `dashboard_api` in the current directory? Inside it, just drop a clean JSON file (name it whatever) with the total fuel spend, total miles driven, and the name of the city with the longest single idle time. I don't care about the exact JSON keys as long as it's standard and the three pieces of data are obviously there. 

I'm begging you, take your time and write a solid script to dig through this. Don't try to guess it, there's way too much data! Thanks a million!
