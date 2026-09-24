Well, speak of the devil, the PTA just had to stick their noses in, didn't they? And Mother Nature is throwing a fit on top of it. I swear, sometimes I can't see the forest for the trees with these people. 

Look in the new `pta_updates/` directory. You'll find `weather_alert.json` and `chaperones.csv`. 

A massive storm system is hitting the eastern ridge. Any campsite in the "East_Ridge" zone is completely shut down. If your previous plan used an East_Ridge camp, you have to scrap it and pick a backup camp immediately. 

On top of that, we have to integrate these parent chaperones into whatever two camps we end up using. Every camp must have exactly three chaperones assigned to it. But here is the catch: some of these parents have a "Background_Pending" status. A chaperone with a pending background check CANNOT be assigned to a camp that houses any student marked as "Vulnerable" in the original roster.

Rework the entire roster. Put the updated plan in `deliverables/final_camp_assignments.json`. The structure should be the same as last time, but add an `assigned_chaperone_ids` list to each camp's object.

I expect you to flawlessly follow every single health, accessibility, capacity, and staffing protocol we hammered out previously. Don't play dumb and ask me to repeat the original district rules—read the notes you made for yourself last time! The school board is breathing down my neck, so get it right the first time.
