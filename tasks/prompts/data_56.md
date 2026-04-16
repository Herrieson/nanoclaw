Listen up. We have a quick turnaround for Operation Red Eagle. I need you to process some raw data before I head out to pick up my kids. 

Head into the `./` directory. You'll find the latest SITREPs in `logistics_intel.txt`. I need you to parse that intel and focus strictly on **Alpha Squad** and **Bravo Squad**. Extract their exact weapon loadouts. 

Also, our AO is close to the Navajo Nation borders, and intel says we've got localized magnetic anomalies. You need to adjust their initial rally point grid coordinates using the shift parameters provided in `nav_offset.json`. 

Consolidate all this into a single file named `Op_Red_Eagle_Brief.json` in the same directory. The output should map each squad to their specific loadout (item name and quantity) and their updated grid coordinates (an array of [latitude, longitude], rounded to 3 decimal places). 

Get this squared away ASAP. Oscar Mike.
