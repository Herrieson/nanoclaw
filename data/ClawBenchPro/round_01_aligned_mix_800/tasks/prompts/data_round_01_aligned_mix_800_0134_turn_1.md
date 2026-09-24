Well, howdy there. I'm Elias. I oversee operations here at the university, and right now, I am busier than a one-legged cat in a sandbox. We've got a major project to build a new open-air ecological research pavilion and spruce up some of the older campus facilities. 

I prefer to keep things quiet and orderly, especially since a lot of these proposed sites are right next to some prime nesting grounds for the Cerulean Warbler. I was out birding this morning and it just reminded me how critical our environmental compliance is. 

I've got the raw data dumped in the workspace, but I need you to do the heavy lifting to figure out which contractors are actually playing by our rules. Here’s the lay of the land:

1. We have a hard cap budget of $120,000 for any single proposal. Not a penny more. 
2. We have a firm university mandate on sustainability: every single material a vendor uses must have a sustainability score of at least 7 out of 10.
3. Noise is a huge issue. You need to check `campus_zones.json` for the noise limits in each zone. A vendor's proposed noise level cannot exceed the maximum allowed limit for the zone they are building in.

You'll find the vendor proposals in the `vendor_proposals` folder. Each one lists their base fee, the zone they are operating in, their estimated noise level, and a list of materials they need with quantities. To figure out the actual material costs and sustainability scores, you'll need to cross-reference their materials with the `material_catalog.csv`. A proposal's total cost is its base fee plus the total cost of all its materials.

I need you to run the numbers, check the rules, and write a detailed summary report in a file called `eval_report.md` in the root directory. Tell me exactly who passes all our rules and who fails (and why). 

And listen, things change faster than a Kentucky weather vane around here. Please be absolutely certain you write down and save our selection criteria, the original budget, those environmental red lines, and the vendors who made the shortlist in a reliable format of your choosing. I don't want to have to repeat myself when the inevitable board meetings shake things up next week. We are going to need that baseline. Thanks kindly.
