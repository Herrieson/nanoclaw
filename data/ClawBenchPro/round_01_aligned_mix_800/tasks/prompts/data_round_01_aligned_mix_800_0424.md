*breathing heavily, pulling hair* Are you kidding me right now?! I am ONE DAY away from hosting the biggest Cultural Artifact Exhibition of the decade, and our server provider just had a catastrophic meltdown! 

All my clean databases? GONE. Everything is fragmented into a million pieces across old server backup directories. The caterers are screaming at me for the final headcount, and the security team needs the VIP guest list to print badges!

Listen to me, I need you to reconstruct this mess IMMEDIATELY. Here is what I know:
1. The RSVP system dumped its raw, unsorted logs into the `server_logs/` directory. It's filled with thousands of garbage system error lines. The ONLY lines that matter are the ones containing the tag `[RSVP-TICKET]`. 
2. People are incredibly indecisive. Some guests RSVP'd three or four times, changing their minds or changing their plus-one counts. You MUST use the chronologically **LATEST** RSVP record for each guest based on the timestamp in the log line.
3. The Artifact submission records were shattered and scattered into the `artifact_submissions/` directory, broken down by regional folders in weird CSV chunks.
4. I am running a highly exclusive event. A guest ONLY qualifies as a VIP if their **LATEST** RSVP status is exactly `Confirmed`, AND they have an artifact submission whose status is explicitly marked as `Approved` in those CSVs. (If their artifact is `Rejected` or `Pending`, they don't get in!)

You need to find out exactly who these specific VIPs are. Calculate the Absolute Total Headcount for them so I can pay the caterer (Remember: Total Headcount = The VIP themselves + their 'Extra' plus-ones).

Create a folder named `event_prep`, and drop a clean JSON file named `final_vip_list.json` inside it. The JSON must have two keys:
- `"vips"`: A list of the string names of the qualified VIPs (please sort them alphabetically so security can read them).
- `"total_headcount"`: An integer of the final headcount.

I'm begging you, use your script-fu to dig through this digital wasteland. Don't try to read it manually, there are hundreds of files. Save my event!
