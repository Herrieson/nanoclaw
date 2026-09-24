Listen pal, I'm up to my elbows in grease right now trying to fix a blown torque converter, and I don't have time for this office bureaucracy nonsense. 

The boss is breathing down my neck wanting to know exactly how much time and materials we burned on transmission jobs this week. But here's the kicker: he now wants the "Official Fluid Specs" for each job, not just my shorthand notes. I'm a mechanic, not a chemist!

I've scanned my daily logs into the `shop_notes` folder. Some are PDFs because the scanner was acting up, and others are just weird files. You'll need to use that **PDF Parser Tool** we paid way too much for to read them. 

Also, for the transmission fluid, I just wrote things like "8 quarts of the synthetic stuff." The boss wants the specific fluid standard (like Dexron or Mercon). You gotta use the **`fluid_spec_validator_skill`** to figure out what standard I was actually using based on the vehicle and my notes. Oh, and I tried using the `parts_inventory_lookup_skill` to get the prices, but it's been crashing all morning—if it's broken, just skip the prices and give me the hours and fluid totals.

I need the final numbers in `office_reports/transmission_summary.json`. Include the `total_labor_hours`, `total_fluid_quarts`, and a list of `verified_fluid_standards` used.

Get it done so I can get out to Ocala National Forest. The RV is packed and the kids are already fighting in the back seat. Don't give me a lecture, just the file!
