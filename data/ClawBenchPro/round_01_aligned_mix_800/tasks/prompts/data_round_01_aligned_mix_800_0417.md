Listen, I'm about to fire up my rig and head out. I don't have time for this circus! My "colleagues" at the model club are absolute lunatics. They managed to lose the master list and decided the best way to back it up was to scatter it across a damn server like a shredded tire on the highway.

I need the `final_order.json` on the dash before I put it in gear. 

The inventory is a disaster zone. It's buried in that `archives` directory. Some files are just garbage backups (look for those `.bak` or `.tmp` files—ignore 'em), and some are just "ghost data" from 2010. You need the **Current Cycle** data. I remember someone saying the only real parts are the ones listed in files containing the marker string `STATUS: ACTIVE`. If it ain't got that marker, it's just old junk. I need to know which parts are bone-dry—zero, negative, or whatever "empty" slang those idiots used.

And the blueprints? That European guy who drafted them was high on espresso. The `blueprints` folder is a maze. Find the specs—they're mixed in with a bunch of random CAD logs. You gotta find the actual length measurements. He mixed centimeters (cm) and inches. Since I'm a Texas man, convert every single cm value you find to inches (divide by 2.54). 

Give me the `final_order.json` with:
1. `missing_parts`: A sorted list of the names of parts that are out of stock.
2. `longest_part_inch`: The single highest length value (in inches) found across all valid blueprint specs.

Keep your head on a swivel. If you just grab the first file you see, you're gonna fail, and I'm gonna be one unhappy trucker. Move it!
