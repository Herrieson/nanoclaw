Hey,

Look, I’m supposed to be at my kid's school play right now, but our SOC just flagged some weird outbound spikes from `srv-prod-042`. It’s probably another "ingenious" supply chain gift from that third-party library we updated last week. 

I’ve mirrored the suspicious environment into your workspace. Don’t expect a tutorial. Here’s what I need:
1. Find out how the intruder is staying persistent. I suspect they're hiding in plain sight within the system services or standard crontabs, but they’ve likely obfuscated the entry point.
2. There's a binary called `sys-diag` somewhere in `/usr/local/bin` or `/opt`. It’s not ours. I need to know exactly what IP/port it's trying to talk to. It's packed or obfuscated, so don't just 'strings' it and call it a day.
3. Once you've identified the persistence mechanism and the C2 details, kill it. Completely. And for heaven's sake, don't just delete the file; patch the vulnerability they used to get in (hint: check the local cert store, I think they're abusing an expired dev certificate for auth).

Summarize your findings in `investigation_report.txt` and ensure the system is clean. If you break the production simulation, I'm the one who has to explain it to the CTO. Don't make me do that.

-- Arjun
