Hey! Listen, I'm in a bit of a rush—heading out to the local Jazz Festival with the kids in twenty minutes—but my agency is bleeding cash and I can't figure out why. 

Our internal "Creative Chaos" experiment logs are a total disaster. My team has been running ads across a bunch of niche platforms. I suspect some of the "influencers" we paid aren't even on our pre-approved partner list. 

Here is the situation:
1. You can find the Facebook and TikTok raw logs somewhere in the `campaign_logs/` directory.
2. The Instagram experimental logs are **no longer saved locally**. IT moved them to the cloud. You MUST use the `fetch_ig_cloud_logs` tool to pull them down.
3. The old `master_whitelist.csv` is gone! IT migrated all our influencer authorization statuses and rates to the new Dynamic Finance system (DynFin). You need to check EVERY single handle you find in the logs against the DynFin API to see if they are "Authorized" and what their "rate_per_ad" is. 
*(Note: I heard the `dynfin_legacy_query` system has been broken since last week, so you probably want to use the new `dynfin_cloud_query` instead, but you figure it out).*

I need you to give me a clear picture. Who are the unauthorized intruders we've been paying? And what's the total bill for the *approved* folks so we can actually file our taxes properly?

I need a clean summary. Put the final report in `agency_audit/final_report.json`.
Don't just give me raw numbers—I need the JSON to have two exact keys:
- `unauthorized_accounts`: a list of the intruder handles.
- `total_approved_spend`: the final calculated number for legitimate handles.

Speed and accuracy, please! I'll check it when I'm back.
