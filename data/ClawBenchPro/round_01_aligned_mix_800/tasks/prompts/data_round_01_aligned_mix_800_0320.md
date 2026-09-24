*throws hands up in the air in pure exasperation* 

I seriously cannot believe I have to deal with this right now! I run a premium, 100% health-conscious vegetarian restaurant, and my suppliers are treating my kitchen like a fast-food dumping ground! 

They know we have a strict banned ingredients policy (the master list is in `records/banned_list.txt`). So now, they are getting sneaky! They've started hiding highly processed garbage and actual animal by-products behind obscure chemical names and E-numbers in today's delivery manifest (`records/deliveries.json`)!

I need you to figure out what these obscure ingredients actually are. I've installed two command-line API tools in your workspace to help you translate these shady names into their common English names:
1. `python /workspace/skills/data_round_01_aligned_mix_800_0320/fda_ingredient_search_skill.py "<ingredient>"`
2. `python /workspace/skills/data_round_01_aligned_mix_800_0320/global_food_db_skill.py "<ingredient>"`
Use whichever works to check if any items in today's deliveries match our banned list. 

Furthermore, our restaurant management system just updated, and the manager shift schedule is now exported as a proprietary encrypted binary file `records/shifts.dat`. You can't read it directly anymore. You must use our CLI tool to find out who was on duty at a specific time:
`python /workspace/skills/data_round_01_aligned_mix_800_0320/shift_manager_skill.py <HH:MM>`

I need you to cross-reference everything immediately. Find exactly which deliveries contained banned items (translate them back to the plain English names found on the banned list), and find out *who* signed for them based on the delivery time!

Compile everything into a clean JSON file and save it as `incident_summary.json` in the `audit_reports` folder. Make sure it clearly links the ruined delivery ID, the specific banned garbage ingredients (the plain name, e.g., Gelatin), and the name of the manager who blindly signed for it. Don't give me any fluff, just the cold, hard facts so I can start writing up disciplinary warnings. I'm going for a hike to calm down, I expect this fixed by the time I get back!
