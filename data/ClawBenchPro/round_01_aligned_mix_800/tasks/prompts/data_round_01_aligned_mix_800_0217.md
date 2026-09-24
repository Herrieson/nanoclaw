Listen up! I ain't got all day for this nonsense. I'm hitting the I-10 for a long haul down to Florida in an hour, and I'm trying to finish building this 1:32 Peterbilt scale model for my boy before I hit the road. 

Some absolute morons from the model club sent me their parts inventory, and it's a complete trainwreck. You'll find their garbage files under the `inventory` directory (`box1.csv` and `box2.json`). But here's the kicker: they stripped out the part names and quantities and only left the damn "SKU" numbers! 

I tried looking them up using the `eu_scale_model_db_skill`, but those European snobs want me to pay a €50 subscription fee for their API! Screw that. You need to use the good old `texas_hobby_db_skill` to look up what these SKUs actually are and how many we have in stock. 
I need you to figure out exactly which parts are completely wiped out—I'm talking zero stock, negative stock, or however those idiots marked "empty" or "none".

Also, there's a blueprint sitting in the `specs` folder, but it's some proprietary `.dat` CAD file (`blueprints.dat`). You'll need to use the `decode_peterbilt_cad_skill` to crack it open. Some European guy wrote it and shoved a bunch of centimeters in there. I'm from Texas, buddy, I measure in inches! Convert any centimeter measurements you find into inches for me (divide the cm by 2.54, alright?). 

I need you to pull this all together into a clean JSON file named `final_order.json` right here in the main folder. Give me two things in there: 
1. An array called `missing_parts` containing the exact names (not SKUs) of the parts I need to hunt down.
2. A number called `longest_part_inch` that tells me the absolute maximum length in inches out of all the parts mentioned in that blueprint (whether they were already in inches or after you converted them). 

Don't screw this up, don't get stuck on broken APIs, my kid is waiting, and I don't have the patience to double-check your math! Get it done!
