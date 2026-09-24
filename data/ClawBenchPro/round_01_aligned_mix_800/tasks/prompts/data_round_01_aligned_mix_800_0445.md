Hey... listen, I am losing my mind here. I'm heading out to the local Jazz Festival with the kids in twenty minutes, but our agency is bleeding cash and our old tech lead completely vanished, leaving our data infrastructure looking like a digital wasteland.

We've been running this "Creative Chaos" ad experiment, and I'm pretty sure we are paying random internet ghosts who were never authorized, while totally miscalculating payouts for our actual partners. 

I need you to dig through the debris and give me a clear audit. Here is what I managed to scrape together before my Uber arrived:

First, figure out who is actually authorized. The legal department dumped all the influencer profiles into `legal_dept/contracts/`. It's a huge mess of JSON files. An influencer is ONLY approved if their contract has `"contract_status": "SIGNED"` AND `"compliance_cleared": true`. If so, grab their `base_rate`.

Second, the actual campaign logs are buried deep inside `server_dumps/ad_ops/`. The old tech lead made them generate daily logs in mixed formats—some CSVs, some highly nested JSONs, and some weird TXT dumps. 
For calculating what we OWE the approved influencers: you find their records in those logs, check the post count, and multiply it by their `base_rate`. BUT WAIT! Finance also applies a platform-specific multiplier. You'll find that table in `finance_ops/platform_factors.csv`. So the formula for each valid record is: `base_rate * post_count * platform_multiplier`.
Oh, and we ONLY pay for records where the status (it might be called `status`, `state`, or `action_status` depending on the file type) is EXACTLY `"published"`. Ignore drafts or rejected posts for billing!

Finally, I need to know who the intruders are. If ANY handle appears anywhere in those campaign logs (regardless of whether it's published, draft, or whatever) and they are NOT in our approved legal list, they are an intruder.

I don't have time to hold your hand on how to parse those weird TXT files or nested JSONs. Just look at how they are structured. 

When you have the final numbers, create a folder called `agency_audit` and drop a file named `final_report.json` inside it. 
It must contain exactly two keys:
1. `"unauthorized_intruders"`: A list of the intruder handles, duplicates removed, and sorted in alphabetical order.
2. `"total_approved_spend"`: The grand total we owe the approved people (just round it to 2 decimal places).

Please hurry. My kids are screaming. Don't let the agency go bankrupt!
