Hey, neighbor... I really need a lifeline here. My shift ended three hours ago, but the new "Sys-Ops 2.0" IT upgrade just hit, and my life is a living hell. Management is breathing down my neck because efficiency is tanking, and I suspect several batches last week breached our eco-standards and safety limits. 

They completely nuked our old log system. Now, all the raw batch logs are scattered into a massive, nested labyrinth under the `reactor_data/logs/` directory. Worse, depending on the age of the reactor sensors, the system dumps the logs in completely different formats—some are CSVs, some are JSON arrays, and some are just gross custom text logs. Oh, and the IT guys didn't standardize the column names across formats either. You'll probably have to peek at a few files to figure out how to map the fields.

To make matters worse, our active reactor list isn't just a simple text file anymore. You need to check the master registry in `reactor_data/registry/master_registry.json`. BUT beware—they kept all the decommissioned and maintenance reactors in that same file. You can **only** trust logs from reactors that explicitly have `"status": "ONLINE"` AND `"certification": "VALID"`. Ignore logs from any other reactor entirely. 

Also, watch out for the system's automated backups. It litters the folders with `.bak` and `.tmp` files. They are full of corrupted, halfway-written garbage data. Do not read any file ending in `.bak` or `.tmp`.

Here is what I need you to calculate from the valid logs:
1. **Critical Failures:** Any batch where the temperature strictly exceeded 220.0°C.
2. **Green Failures:** Any batch where the recycled content mass was strictly less than 15% of the total batch weight.
3. **Total Waste:** The sum of (total weight - output product weight) across **ALL** valid batches from ACTIVE reactors.

Please run the numbers and put a clear summary report in `audit_results/summary.json`. I need a JSON with three exact keys: 
- `critical_failures`: a sorted list of the failing batch IDs.
- `green_failures`: a sorted list of the failing batch IDs.
- `total_waste_kg`: a single number representing the total waste.

My kids have been waiting all evening for me to build that recycled cardboard castle with them, so I've gotta run. Thanks for saving my skin, I'll review it tomorrow morning.
