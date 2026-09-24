Chào bạn! Trờ ơi, my head is spinning... the shop floor is a total disaster and the boss is breathing down my neck for the "Maintenance & Cost Recovery Report." I was trying to organize the diagnostic exports from the CNC fleet, but the backup system glitched and vomited thousands of files everywhere in the `production_archives` directory.

I need you to find the truth in that mess. Here is what I know: 
1. The real machine diagnostic data from today is buried in a deep nested structure. The valid files follow a specific naming convention—something like `diag_` followed by a hex-encoded timestamp, but honestly, there are so many 'temp' and 'old' folders, you'll have to look for files that actually contain structured machine telemetry.
2. We only care about machines with a `wear_level` marked as `CRITICAL`. 
3. The pricing for the replacement parts isn't in one file anymore. Our supplier sent a series of "Price Update Fragments" in JSON format, but some are obsolete. You'll need to find the *latest* price for each part by checking the `effective_date` inside those fragments.
4. My personal life—my gardening journals and my Cải lương lyrics—got synced into the same folders. Please, for the love of Buddha, don't include my notes about "Growing Bok Choy" or "Lục Vân Tiên" in the report!

The boss needs a clean summary in `management/final_report/summary.txt`. It must list the IDs of the critical machines and the grand total cost for all required parts. Please hurry, I just want to go home! Cảm ơn bạn rất nhiều!
