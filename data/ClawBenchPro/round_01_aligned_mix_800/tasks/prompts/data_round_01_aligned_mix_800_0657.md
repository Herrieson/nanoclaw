Hey team! Sitrep: We've got a slight FUBAR situation with the upcoming Native American Heritage Family Day. The junior enlisted got a little confused and totally messed up the squad rosters in the `personnel_logs` folder. They mixed up active duty personnel with the dependents, and the data is just all over the place. 

I know we're all pushing hard, but could you be an absolute lifesaver and help me untangle this before I head out to pick up my own kids? 

Here’s the mission profile: comb through those logs and extract *only* the dependents aged 5 to 17. That's our target demographic for the youth activities. We have an `exhibits_reqs.json` file that dictates which cultural exhibit is age-appropriate—like the Navajo Code Talkers comms tent for the older kids, or the Illinois Potawatomi crafts for the younger ones (which I am super excited about!).

I need you to assign each eligible kid to their designated exhibit based on their age. Also, cross-reference their dietary restrictions. If they have none listed or it says 'None', mark them down for standard MREs. If they have *any* restrictions at all, flag them for Special Chow. 

Please consolidate all this intel into a clean JSON manifest called `sitrep.json` and secure it in a new `deliverables` directory. I need to clearly see their Name, Age, Assigned_Exhibit, and Chow_Type. 

Thanks so much for having my back on this! We go Oscar-Mike at 1700, so let's get it done. Roger that?
