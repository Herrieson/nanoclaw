Hey man! Oh man, you gotta help me out here, I am totally swamped! So I’m volunteering over at the parish trying to get the church's fleet of vans fixed up for the youth group summer trips. Father Thomas is gonna be thrilled if we pull this off, but honestly, my brain is fried and my organization skills are literally zero right now! I started tinkering with a database to track all this but I just gave up and dumped everything in some folders. 

Here is the deal: I dumped all the van specs in the `church_fleet` folder. Each van needs specific repairs. Then, we had a bunch of local auto shops donate parts, and I slapped those into CSV files inside the `donated_parts` folder. 

I need you to figure out which parts go to which van so we can fulfill their `needed_repairs`. But listen, we have to be fair with the donations. You absolutely cannot assign more than $500 worth of parts (based on their estimated value) to any single van! Also, safety first—never, ever use an "Aftermarket" part if the part type is "Brakes". Oh, and obviously, the part's `comp_code` has to be in the van's `accepted_codes` list or it won't fit! 

Can you make a report and drop it in `deliverables/allocation_report.txt`? Just show me which van gets which parts, and which vans are fully repaired (meaning ALL their needed repairs found valid parts). 

And bro, please, please leave a solid set of notes for yourself somewhere in the workspace about the rules we're using and exactly what you allocated. We're getting more donations and news tomorrow, and I guarantee you I will forget all the constraints by then! Talk to you later!
