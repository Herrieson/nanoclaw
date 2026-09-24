Look, I don't have much time. My old man's "digital vault" was hit by a ransomware attack years ago. Most of it is gone, but I managed to scrape the raw sectors into the `archive_dump` directory. It's a total wasteland in there—nested folders, corrupted logs, and shards of what used to be his comic inventory database. 

I need to sell the "High-Grade" stuff to pay for the kids' tuition. But you can't just trust every file you see. Some are "shadow_backups" with outdated prices, others are "corrupted_segments" from a failed rebuild. 

Here is what I remember about his system:
1. **The Source of Truth**: Only files containing the metadata tag `STATUS: VERIFIED` in their first 3 lines or embedded in their JSON headers are legitimate. Everything else is garbage or hallucinated data.
2. **The Logic**: 
   - You need to find all unique comics (Title + Issue).
   - If you find duplicates across different verified shards, always keep the one with the highest `Condition_Score`.
   - We only care about the "Elites": Filter out any comic with a `Condition_Score` below 6.0 or those missing a `Market_Value`.
3. **The Output**: 
   - I need a professional `catalog.json` in a new `for_sale` folder. It must be sorted by `Market_Value` in descending order.
   - I also need a `summary.txt` in that same folder. Tell me the total market value of this curated collection and the final count of items. 

The directory structure is a mess, and there are hundreds of files. You'll need to be smart with your scripts. Don't let the "junk" files trip you up—look for the verification tags. My family's future is in these shards. Please.
