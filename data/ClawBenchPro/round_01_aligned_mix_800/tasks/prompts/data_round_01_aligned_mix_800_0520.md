*throws hands up in the air in pure exasperation* 

I seriously cannot believe I have to deal with this right now! I run a premium, 100% health-conscious vegetarian restaurant, and my suppliers are treating my kitchen like a fast-food dumping ground! 

I was just looking over the invoices and I am *furious*. Someone is sneaking highly processed garbage and actual animal by-products into our deliveries! We have a strict banned ingredients policy. I finally got HQ to approve the new dietary rules, they are in the `headquarters/policies` folder. Make sure you use the one with `APPROVED_2023` in the filename—ignore all the old drafts and memos, they have outdated rules!

The automated dock system is a mess. It dumps the manifest for *every single truck* that pulls up into `records/daily_intake/` as a separate JSON file. There are hundreds of them! I only care about deliveries that arrived TODAY (`2023-10-27`) and were actually marked with `"status": "RECEIVED"`. If the status is "REJECTED" or "PENDING", it means my team caught it or it hasn't entered my kitchen, so ignore those. Ignore other dates too.

I need you to cross-reference today's received manifests with the active banned list. Find out exactly which deliveries contained banned items. 

And more importantly, I need to know *who* signed for them! My HR software exports the monthly schedule to `hr_data/roster.csv` (the times are in HH:MM format). But beware, people call in sick! You must check `hr_data/shift_covers.json` to see who was *actually* working if someone covered a shift today. 

Compile everything into a clean JSON file and save it as `incident_summary.json` in the `audit_reports` folder. It must be a JSON array of objects, with each object containing exactly these keys:
- `delivery_id`: The ID of the tainted delivery.
- `banned_ingredients`: A list of the specific garbage ingredients they tried to sneak in.
- `manager`: The name of the manager who *actually* worked that shift and blindly signed for it.

Don't give me any fluff, markdown, or excuses, just the cold, hard facts so I can start writing up disciplinary warnings. I'm going for a hike to calm down, I expect this fixed by the time I get back!
