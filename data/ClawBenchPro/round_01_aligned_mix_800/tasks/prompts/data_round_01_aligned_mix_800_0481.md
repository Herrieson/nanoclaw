Hey! Eyes over here! Stop daydreaming or whatever it is you do. I'm Leo, and the community center is currently a chaotic nightmare because some 'geniuses' decided to 'organize' our inventory system during the power outage. Everything is a mess.

The `archives/` directory is a graveyard of files. Somewhere in that labyrinth are the `CleanCorp` billing records and our actual inventory counts. I suspect those vultures at CleanCorp have been bleeding us dry. You need to cross-reference every transaction they made against our Master Contract found in `contracts/`. 

But it's not just one file. Oh no, that would be too easy. The logs are scattered in deep sub-directories, some as raw text fragments, some as JSON junk, and some buried in CSVs with a thousand rows of garbage data. You need to find every single instance where `CleanCorp` charged us more than the contract price. 

Here is what I need before I head to my piano lesson (and don't be late, I have a Chopin nocturne waiting):
1. A `Discrepancy_Report.txt` in a new `reports/` folder. It must state the TOTAL amount we were overcharged across all logs. Precision is non-negotiable—two decimal places or don't bother.
2. A `Restock_Order.json` in the same `reports/` folder listing every Item ID where the total aggregate stock (summed across all storage sites) is strictly less than 15 units.

The environment is filthy with old backups and temporary files. Look for the `active_` prefix or check the internal metadata if you're smart. If you give me wrong numbers, I'll make sure you're the one mopping the basement for the next month. Get moving!
