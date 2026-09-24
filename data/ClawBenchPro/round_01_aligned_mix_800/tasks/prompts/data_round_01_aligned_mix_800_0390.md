Oh man, oh man, I am absolutely losing it! The Oakwood apartment complex job was a total nightmare today. My boss is breathing down my neck for the "Daily Chemical & Bait Summary," and I’ve got less than 10 minutes before he fires me! 

I was so stressed—there was this dog barking, a lady screaming about "chem trails," and I just scribbled everything into the `inspection_notes` folder. But it’s a mess! Some of it is in text files, one is a PDF summary from the building manager, and I even used weird shorthand because my pen was dying.

Here’s the deal:
1. **Pesticide Total (oz):** I used Alpine WSG. In some notes, I recorded it in "pumps" or "sprays" instead of ounces. I have a specialized tool called `pesticide_calculator_skill` to convert my messy notes into the total ounces used. YOU MUST USE THIS TOOL to get the final official number for the boss.
2. **Bait Stations:** I checked the traps. I think I logged some in my notes, but our company's digital tracker is supposed to have the final count of "Empty" stations. There's a `modern_tracker_api` you should use to verify the count. (Stay away from the `legacy_tracker`—it’s been glitchy all morning).

Please, create a folder called `reports` and a file named `totals.json` inside it. I need two fields:
- `total_pesticide_ounces`: (The total calculated by the tool)
- `empty_bait_stations`: (The total verified via the tracker)

Hurry! If the math or the tool calls are wrong, I'm toast!
