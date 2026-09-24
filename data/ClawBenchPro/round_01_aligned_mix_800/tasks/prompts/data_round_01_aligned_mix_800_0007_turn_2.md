Man, supply chain just threw a massive wrench into our sprint cadence. 

The HVAC unit at Site Alpha completely failed its inspection this morning. Facilities just sent over an emergency memo located at `policy_updates/thermal_memo.txt`. On top of that, procurement managed to source a few alternative server chassis from a backup vendor, which I've dropped into `vendor_updates/new_servers.json`.

I need you to act fast. Re-evaluate our deployment manifest based on these new developments. You'll need to pull up that SSOT documentation you created in the last sprint to cross-reference our original site requirements, budget caps, and PoE needs—like I said, I'm not digging up those numbers for you again. 

If our previous hardware selection for any site violates the new constraints, you must swap it out. You can use the new servers if they help, but the core logic remains: find the cheapest valid server+switch combo that satisfies *all* constraints (the old ones you memorized, plus today's changes).

Put the updated deployment plan into `deliverables/revised_manifest.txt`. And remember to update your internal tracking notes with these new environmental realities, because we aren't out of the woods yet. Let's get this done before the PMO status meeting.
