Mon Dieu, I really cannot deal with everyone's noise today. My family expects the parish retreat camp to be perfectly safe by the weekend, but no one actually does the heavy lifting except me.

I need to go for a trail run to clear my head. While I'm gone, please sort out this mess. I've left the basic trail logs in `raw_logs/trail_reports.txt`, but our old safety officer moved the actual hazard assessments into the new **Parish Terrain Analysis System**. You'll need to use the `terrain_risk_analyzer` tool to get the real danger levels for each trail. Anything with a hazard level strictly greater than 3 is a priority.

Also, the volunteer roster is stuck in an old legacy database format (`raw_logs/volunteers.db`). You'll need the `legacy_db_extractor` to get their skills. I only want volunteers who have "clearing" skills.

I need a file named `action_plan.json` inside a new `output` folder. It must contain:
1. `dangerous_trails`: A list of objects, each containing the trail name and the specific "recommended_tool" (the analyzer tool will tell you this).
2. `capable_volunteers`: A list of names of volunteers who can handle clearing.

And because I need to *see* the danger to believe it, draw a simple ASCII bar chart in `output/hazard_chart.txt` showing the hazard levels of those dangerous trails.

Don't bother me with questions. Just use the tools and get it done.
