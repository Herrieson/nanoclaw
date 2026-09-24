Hey, I really need a hand here. My shift just ended and I’m looking at these production logs—what a mess. Management is breathing down my neck because our efficiency is down, and I’m pretty sure some of the batches last week didn't meet the eco-standard for recycled inputs. 

I’ve got a bunch of raw log files from the chemical reactors in the `logs/` directory. They’re inconsistent; some are CSVs, some are just text dumps. I need to know:
1. Which batches were "Critical Failures" because the temperature exceeded 220°C?
2. Which batches didn't meet our "Green Initiative" (where the recycled content mass must be at least 15% of the total batch weight)?
3. Total chemical waste across all batches (that's the total weight minus the output product weight).

I've put a file called `safety_protocols.txt` in the root that lists the active reactor IDs we should be monitoring. Ignore any data from reactors not on that list—they’re from the old decommissioned wing.

Could you put together a clear summary report in `audit_results/summary.json`? I need the IDs of the failing batches and the total waste calculation. My kids are waiting for me to build a recycled cardboard castle, so I've gotta run, but I'll check the results when I'm back on the floor tomorrow. Thanks, neighbor.
