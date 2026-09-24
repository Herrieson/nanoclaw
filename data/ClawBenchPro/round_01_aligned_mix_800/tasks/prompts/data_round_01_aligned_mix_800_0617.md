Listen up! I ain't got all day for this nonsense. I'm hitting the I-10 for a long haul down to Florida in an hour, and I'm trying to finish building this 1:32 Peterbilt scale model for my boy before I hit the road. 

Some absolute morons from the model club sent me their parts inventory, and it's a complete trainwreck. You'll find their garbage files under the `inventory` directory. I need you to comb through that mess and find out exactly which parts are completely wiped out—I'm talking zero stock, negative stock, or however those idiots marked "empty". 

Also, there's a file called `blueprints.txt` sitting in the `specs` folder. Some European guy wrote it and shoved a bunch of centimeters in there. I'm from Texas, buddy, I measure in inches! Convert any centimeter measurements you find into inches for me (divide the cm by 2.54, alright?). 

I need you to pull this all together into a clean JSON file named `final_order.json` right here in the main folder. Give me two things in there: an array called `missing_parts` containing the exact names of the parts I need to hunt down, and a number called `longest_part_inch` that tells me the absolute maximum length in inches out of all the parts mentioned in that blueprint (whether they were already in inches or after you converted them). 

Don't screw this up, my kid is waiting, and I don't have the patience to double-check your math! Get it done!
