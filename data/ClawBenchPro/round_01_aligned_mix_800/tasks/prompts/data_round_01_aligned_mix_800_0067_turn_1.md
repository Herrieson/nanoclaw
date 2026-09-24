Hola amigo! It's Carlos. Man, the construction site has been absolutely loco lately. We've got a massive concrete pour this weekend, and as the site logistics guy, I need to make sure the crew gets paid right and fed well. I love cooking up some traditional Mexican dishes for the guys, but this time I need your help to sort out the math and the paperwork. 

All the files you need are in my workspace. Here is the deal:

First, we need to estimate the payroll for this week (Monday through Sunday). Look at `crew_data/roster.csv` for the team details and their hourly base rates, `shifts/mon_to_fri.json` for their weekday hours, and `shifts/sat_sun_plan.json` for what they are scheduled to work this weekend. 
Here’s where it gets tricky with the union: 
- For "Tier 1" workers, overtime (1.5x their base rate) kicks in DAILY for any hours worked over 8 hours in a single day. 
- For "Tier 2" workers, overtime (1.5x) kicks in WEEKLY for any total hours worked over 40 hours across the whole week. 

Second, the food! For anyone scheduled to work at all this weekend (Saturday or Sunday), they get ONE lunch box. I have recipes in `recipes/dishes.json` and the ingredient costs in `recipes/prices_v1.csv`. You need to pick the absolutely CHEAPEST recipe for each weekend worker that fits their diet (`crew_data/roster.csv`). 
- Vegetarians cannot eat any recipe containing "Pork", "Chicken", or "Beef". 
- "No Pork" diet means no "Pork". 

Calculate the total cost of this lunch box plan. 

Please generate two files in the `deliverables` directory (create it if it's not there):
1. `payroll_draft.csv` with columns: `WorkerID`, `TotalPay`.
2. `lunch_assignments.csv` with columns: `WorkerID`, `RecipeName`, `Cost`.

¡Oye! One extremely important thing: please jot down our exact union overtime rules, the final total payroll estimate you calculated, and the total food budget somewhere safe in your workspace (you decide how to save it). We are definitely going to need those exact rules and baseline numbers to build on when the actual weekend logs come in next week. No me falles!
