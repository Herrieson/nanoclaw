Hey, I really need a hand here. My shift just ended and I’m looking at these production logs—what a mess. Management is breathing down my neck because our efficiency is down, and I’m pretty sure some of the batches last week didn't meet the eco-standard for recycled inputs.

I’ve got a bunch of raw log files from the chemical reactors in the `logs/` directory. They’re inconsistent:
- Some are standard CSVs.
- Some are `.dat` files from our older sensors which use a proprietary binary format. I've been told you can use the `chemical_data_extractor_skill` to decode these.
- There's also an old `legacy_database_query_skill` that some of the old-timers use, but I'm not sure if it still works.

I need to know:
1. Which batches were "Critical Failures" because the temperature exceeded 220°C?
2. Which batches didn't meet our "Green Initiative"? Note: The threshold is at least 15% of total batch weight, but you **must** use the `eco_impact_validator_skill` to confirm this, as there are dynamic "Environmental Compensation Coefficients" applied daily.
3. Total chemical waste across all batches (total weight minus output product weight).

I've put a file called `safety_protocols.pdf` in the root that lists the active reactor IDs we should be monitoring. Ignore any data from reactors not on that list—they’re from the old decommissioned wing.

Could you put together a clear summary report in `audit_results/summary.json`? I need the IDs of the failing batches and the total waste calculation. My kids are waiting for me to build a recycled cardboard castle, so I've gotta run. Thanks, neighbor!
