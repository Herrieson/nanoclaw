*Adjusts sunglasses while leaning against a rusted delivery truck that smells like stale coffee and ozone.*

Look, I’m not saying Dave is incompetent, but I’m pretty sure he’s been using the logistics server to mine some obscure crypto instead of, you know, managing logistics. The "Manifest Depot" is an absolute radioactive wasteland of data right now. He "accidentally" ran a corruption script on the daily batch, and now the delivery records are scattered across hundreds of fragmented files.

I’m the premium handler for **Zone 7**, and I’m losing my mind here. I need to hit the road five minutes ago, but I can't leave without my **Zone 7 route list**. Here is the catch: Dave's "recovery" process created a nightmare. 

The core data is buried in `archive/` and its subdirectories. You'll find thousands of files—logs, fragments, backups. You need to find the **valid manifests**. I know for a fact that valid manifest files contain a specific metadata tag: `SYSTEM_VERIFIED: TRUE`. If that's not there, ignore the file; it’s just junk data or a corrupted ghost from the 2018 archives.

For all the valid records you scavenge, I need:
1. A clean delivery sheet in a new directory `clean_route` named `zone_7_manifest.json`. It must contain *only* Zone 7 packages. **CRITICAL:** The **VIP** packages must be at the very top. I consider a package VIP if its status is marked as 'VIP', 'Priority', 'Level_1', or if the tracking number starts with 'TRK-777'.
2. In the same `clean_route` folder, I need a text file `deviations.txt` containing only the tracking numbers (one per line) of any package you found in those verified files that belongs to **Zone 3** or **Zone 9**. I need to throw those back at Dave's desk.

The data formats are a mess—some are JSON, some are weird key-value pair logs, some are CSV-ish fragments. Just... figure it out. If I miss my kid’s school pickup because I’m staring at a corrupted terminal, I'm holding you responsible. Gracias, and watch out for the legacy junk files; there are thousands of them.
