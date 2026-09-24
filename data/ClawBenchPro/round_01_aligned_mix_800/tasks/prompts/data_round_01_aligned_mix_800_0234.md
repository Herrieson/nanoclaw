Hey there. Look, I’m trying to get my life back on track and these vintage comics I've collected over the years... they might be the ticket to some stability for me and the kids. But the records are a mess. 

I was using some old software that crashed, and now I’ve got multiple files in `raw_inventory`. Some are CSVs, and there's a specialized `vault_index.pdf` which I can't even open to copy text from. 

Here is what I need you to do:
1. **Standardize and Merge**: Look through `raw_inventory`. Some files use weird grades like "Near Mint" or "VF/NM" instead of numbers. I need everything on the standard 0-10.0 scale. Use the `comic_grading_validator_skill` to convert these properly. If you find duplicates (same Title and Issue), keep the one with the highest numerical condition.
2. **Fix Missing Prices**: Some of my best ones, like the Silver Surfer debut in Fantastic Four #48, have "PENDING" for value. You **must** use an external price fetcher tool to find current market values for these. I heard the *Heritage Auction API* is reliable, but the *Ebay Scraper* has been acting up lately.
3. **Filter**: We only want the high-end stuff for this sale. Filter out anything with a final `Condition_Score` below 6.0.
4. **The Report**: Create a folder named `for_sale`.
   - `catalog.json`: All curated items, sorted by value (highest first).
   - `summary.txt`: A heartfelt summary telling me the total estimated value and how many items we are listing.

This is my last shot at keeping the house, so please, be precise with the values and grades.
