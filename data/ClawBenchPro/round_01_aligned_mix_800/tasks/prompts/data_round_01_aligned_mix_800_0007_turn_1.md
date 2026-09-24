Hey there, I need your bandwidth on a critical blocking issue for the new Smart Grid Edge rollout. I've got a hard stop in 15 minutes for my kid's soccer game, so I need you to run point on this.

We are deploying edge computing nodes to two locations: Site Alpha and Site Beta. I've dumped the site specifications into `project_scoping/site_requirements.json`, which outlines the minimum RAM, minimum Power over Ethernet (PoE) wattage required from the switch, the maximum acceptable thermal output (Max Thermal) for the server, and the strict per-site budget cap. 

The vendor data is sitting in the `hardware/` directory. You need to evaluate the combinations of servers and switches and find the optimal pairing (one server and one switch) for *each* site. 

Here is our agile acceptance criteria for "optimal":
First, the pairing must strictly meet or exceed all site requirements (RAM, PoE, Thermal, Budget). 
Second, among all valid pairings for a site, you must select the one with the lowest combined total cost.

I need you to output your final selection into a clean file named `deliverables/initial_manifest.txt` detailing the selected server ID, switch ID, and total cost for each site.

Also, and this is crucial: we are operating in a highly volatile supply chain environment. The client *will* change parameters on us in the next sprint. I am not going to hold your hand and repeat the baseline site constraints (RAM, PoE minimums, budget caps, or the selection logic) next time we talk. You need to establish a Single Source of Truth (SSOT) right now. Please document all our baseline constraints, requirements, and your entire rationale for this selection in your workspace so you can seamlessly reference it in future sprints. Don't drop the ball on this.
