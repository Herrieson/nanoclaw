Listen, I'm heading out to the north pasture to check the irrigation lines before the storm hits. Don't have time for a long chat.

My AgTech gateway dumped last month's soil sensor readings into the `logs` directory. It's a mess—some files are compressed, some aren't. I also have a SQLite database `sensors.db` that tracks where I planted each sensor. 

I'm strictly trying to protect the creek from chemical runoff from the neighboring conventional farm. I need you to find out if any of the sensors located in the "Riparian Buffer Zone" recorded an acidic pH (anything strictly below 6.0). 

Figure out which sensors in that specific zone are affected, find the absolute lowest pH they each recorded over the entire month, and leave a file named `report.json` for me. Just make it a simple JSON dictionary where the keys are the sensor IDs and the values are their lowest recorded pH. 

I don't need any fluff or explanations, just get the data sorted so I can report it to the environmental conservation board tomorrow.
