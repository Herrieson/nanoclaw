Hello there. *waves hand dismissively at the messy desk* I simply don't have the time to deal with this today. The kids will be home from school any minute, and I really must get out to the garden while the sun is still up. 

As you probably know, I handle specialized deliveries, but the dispatch system went completely haywire last week and dumped everything into a disorganized file called `raw_deliveries.txt`. It's a complete mess, and I cannot stand disorder. *adjusts glasses firmly* 

I need you to clean this up for me. Here is exactly what must be done:
1. Extract all the delivery records from `raw_deliveries.txt`. They look like gibberish but I'm sure someone with your skills can figure out how the system encoded them.
2. Each valid record contains a tracking number, a zip code, and a package weight.
3. Cross-reference those zip codes with my local database `zone_map.db`. It contains the delivery rates for our zones.
4. If a zip code isn't in the database, discard that record completely. We don't deliver to unmapped zones.
5. For the valid ones, calculate the revenue for each package (rate multiplied by weight).
6. Create a perfectly formatted file named `consolidated_report.json`. It must contain a list called `deliveries` (with keys `tracking_number`, `zip_code`, `weight`, and `revenue`), strictly sorted by the tracking number in alphabetical order. 
7. At the root level of the JSON, include a `total_revenue` field summing up all the valid deliveries.

*hums a quiet, traditional Protestant hymn* Please be precise. I value hard work and I expect the numbers to match to the penny. Let me know when it's finished.
