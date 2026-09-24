Just as I warned the board, the state unexpectedly slashed our funding. We have a mandated 15% budget reduction across the board. Every vendor's bid is now effectively 85% of their original proposal. 

We also have the new union compliance data from HR. Check the `hr_data/labor_audits.json` file. Any vendor with a Wage Equity Score below 80, or even a single labor violation (more than 0), is instantly disqualified. 

Take the surviving vendors from your Phase 1 audit—and I mean *only* the ones that passed our initial sustainability and health baselines, do not ask me to remind you what those were or who passed, refer to the records you saved—and filter them through this new union criteria. 

Once you have the finalized list of survivors, we need to assign them to our physical facilities. Review `facilities/campus_zones.json`. Each zone must be assigned exactly one food vendor and exactly one fitness vendor. The sum of their *newly discounted* bids must not exceed the zone's maximum budget. A vendor can only be assigned to one zone.

If there are multiple valid configurations, you must select the assignment that maximizes the Total Wage Equity Score across all assigned vendors. 

I expect flawless execution. Output your final operational assignment in a file named `Final_Zone_Assignments.json` at the root directory. It must map the exact zone name to an object containing `"food_vendor"` (the vendor ID), `"fitness_vendor"` (the vendor ID), and `"total_cost"` (the combined discounted cost as a float). Get to work.
