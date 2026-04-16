Hello there! Oh, I am so hoping you can help me out. I'm organizing our secondary school's "Spring Canopy Project" this year—it's a wonderful outdoor community event where the kids get to plant trees and learn about nature. I'm currently trying to put together a nice, clear visual board for the assignments, but I've run into a bit of a snag with the technology side of things. 

The school district's IT department sent me the student sign-ups, but instead of a simple spreadsheet, it looks like a dense thicket of computer jargon! They called it a "server log dump." It's saved in `/workspace/volunteer_logs.txt`. Somewhere in all that mess are the actual sign-ups from the kids, showing what kind of tree they want to plant. 

I also have a little guide I made, `/workspace/tree_guide.json`, which explains what kind of soil each tree prefers. And finally, there's `/workspace/zones.csv`, which lists the different park areas we have available, their soil types, and the maximum number of students each zone can safely accommodate without damaging the local flora.

Could you please untangle this for me? I need a simple, clean file named `assignments.csv` in `/workspace` with three columns: `Student_Name`, `Tree_Choice`, and `Assigned_Zone`. 

Just a few little rules to keep the ecosystem balanced:
1. Make sure each student is only assigned once (some of the kids get excited and click the submit button multiple times!).
2. A tree must be assigned to a zone that has its preferred soil type.
3. Please don't overcrowd a zone! Once a zone reaches its `Max_Capacity`, no more students can be assigned there.
4. If there's no space left for a student's tree in the correct soil, just leave them out of the final file (I'll find another activity for them).

Thank you so much! Having this sorted out will make our event as clear and beautiful as a sunny spring morning. I really appreciate your time!
