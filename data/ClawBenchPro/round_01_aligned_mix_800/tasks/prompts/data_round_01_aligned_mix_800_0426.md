Hey. *sighs and rubs temples* I am this close to firing the new apprentice. I'm trying to build that dining table for my wife this weekend, and I asked the kid to keep a simple ledger of our wood inventory. Instead, he decided to "modernize" our system.

He shattered the logs into hundreds of fragmented files and nested them deep in the `mill_data/inventory_logs` directory by month and week. To make matters worse, he stopped using actual wood names and invented his own cryptic material codes. He claims he left a mapping file for his codes in `mill_data/codes/material_dictionary.json`. You're going to need that to figure out which code means 'White Oak'. 

The logs themselves are a complete mess of CSVs, JSON arrays, and his weird shorthand `.log` text files. And watch out—he left his draft `.tmp` and `.bak` backups scattered in the active log folders. Do NOT read those, their data is wrong. Also, absolutely ignore everything in the `mill_data/archive` folder; that's from last year's inventory and will completely screw up my current numbers.

I need you to write a script to comb through only the valid, active files in `mill_data/inventory_logs`. Find every single board that is exactly `Usable` condition and corresponds to 'White Oak'. Ignore the warped, split, or rotten garbage. 

Calculate the total board feet. Remember: thickness times width times length (they are all in inches), divided by 144. 

When you're done, generate a clean JSON document named `usable_oak_report.json` and put it in the `project_planning` folder. I need a single key `"total_board_feet"` with the total sum, and a `"boards"` array. Each item in the array should just be an object with `"id"` (the item ID from the logs) and `"board_feet"`. 

Write a bulletproof script to dig through this digital scrap pile. No fluff, just find me my White Oak so I can finally fire up the table saw.
