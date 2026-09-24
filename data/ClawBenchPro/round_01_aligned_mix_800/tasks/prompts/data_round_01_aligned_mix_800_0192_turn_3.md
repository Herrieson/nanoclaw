*Taps fingers aggressively* Disaster! Read the `equipment_alert.txt` in the `updates` folder. The main console in Studio A is dead starting Thursday morning.

Look at your current schedule. If anyone is scheduled in Studio A on Thursday or Friday, we have a huge problem because the console they expect is gone. We can either move their session to another day or studio (but ONLY if it doesn't break ANY of our previous rules and band constraints!), or we can rent a replacement console from the catalog I just dropped in `rentals/catalog.csv`. 

Find the absolute cheapest way to resolve this. If renting is the only way to avoid breaking our historical scheduling rules, do it. Put the final schedule in `schedules/final_plan.json` (same format) and write a file `schedules/budget_impact.txt` containing just a single number: the total rental cost in dollars (0 if we didn't need to rent).
