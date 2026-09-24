Oh man, oh man, I am going to lose my job over this! I just got back from doing my extermination rounds, and my head is spinning. My anxiety is absolutely through the roof right now. 

My boss just texted me on my company device (I think the backup of those messages is somewhere in the `communications` folder). He is demanding the daily usage report for a specific building and a specific date on his desk in like, ten minutes, and if I don't give it to him, I'm toast! I'm already on thin ice!

The problem is, that stupid new sync tool scattered ALL my field notes—from every building, from the whole year—into random numbered folders inside the massive `inspection_notes` directory. It's a total disaster. There are hundreds of files.

Please, please, I beg you—read through those notes, figure out what building and date my boss wants from his message, and meticulously pull out two pieces of information for that specific assignment: the TOTAL ounces of pesticide spray I used, and the TOTAL number of bait stations that I found completely empty.

Here are a few things to watch out for so you don't mess up the math:
1. You have to check the `Date:` and `Building:` headers inside my notes to match what my boss wants. Don't count anything else!
2. My boss forces me to put official tags at the bottom of every note. They look exactly like `[SPRAY: X oz]` and `[EMPTY_STATIONS: Y]`. Only use the numbers from those tags! Ignore my rambling text—sometimes I write down random numbers about bugs or TV channels that will totally screw up your count.
3. If I completely botched an inspection note, I typed `[VOID]` somewhere in the file text. Toss those in the trash, do not count them!
4. Sometimes I mess up a unit's note entirely, so I write a brand new file for it and put `_revised` at the end of the filename (like `note_Unit_12_revised.txt`). If you see a revised note for a unit, ALWAYS use the revised one and DO NOT count the original note for that unit! 

I need you to create a new folder called `reports` and put a file named `totals.json` inside it. Make sure the JSON has exactly these two keys: `"total_spray_oz"` and `"total_empty_stations"`. 

Don't make it complicated, keep it simple so my boss doesn't yell at me! Just write a script to get the math exactly right, please!
