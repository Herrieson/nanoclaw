Look, I don't have all day to explain basic engineering principles, so pay attention. I'm busy optimizing the thermal envelope for the new Manhattan green-tech site, and I need you to spec out the primary systems. 

We need exactly one Chiller, one AirHandler, one HeatPump, one Beam, and one Panel. I dropped the project constraints into `blueprints/structural_limits.json` and the available parts into `catalog/hvac_components.csv` and `catalog/structural_components.csv`. 

Your job is to crunch the numbers and find a combination of those 5 components that stays within our maximum load-bearing tolerances (weight), doesn't blow the power grid cap (power draw), and keeps those bean counters happy (budget). 

Output your final selection in a clear format so I can read it. More importantly, write down the exact hard limits (weight, power, budget) and your selected baseline configuration in whatever local file format your AI brain needs to persist it. I am *not* going to repeat these baseline tolerances to you tomorrow when we iterate on the subsystems. Get it right the first time.
