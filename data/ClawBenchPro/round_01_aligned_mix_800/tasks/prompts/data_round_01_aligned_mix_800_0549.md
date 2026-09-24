Hi there. I'm the regional sales manager for a warehouse club here in California, and honestly, I am drowning right now. We're running a massive community donation drive for local schools, but our legacy IT systems are an absolute nightmare and I need to figure out exactly who is missing what before the school boards start complaining.

Here is the disaster I'm looking at:
1. The `requests` folder is a massive dumping ground. Sales reps just throw everything in there. Some files are drafts, some are backups, and many requests were flat-out denied. **Only trust the JSON files that explicitly have a status of "APPROVED" inside them.** Ignore everything else.
2. The warehouse team dumped their actual outbound logs in the `warehouse_logs` directory, broken down into dozens of daily CSV files. 
3. The real headache: The schools requested items using plain English item names, but the warehouse only logs transactions using `SKUs`. Also, they only log the `School_Code`, not the actual school names. I think the IT guys left the master mapping files somewhere in a `reference` directory.
4. Logistics have been messy. Sometimes items get sent out (`SHIPPED`), but the schools turn them away at the door, and they get sent back to us (`RETURNED`). I only care about the net amount of items that *actually stayed* with the schools (i.e., Total SHIPPED minus Total RETURNED). Any other warehouse statuses like 'PROCESSING' or 'CANCELLED' should be completely ignored.

Could you do me a massive favor? I need you to reconcile all this garbage data and tell me exactly what each school is still missing. 
Please create a new `reports` folder and save a file called `missing_items.json`. It should map the **actual School Name** directly to the items and quantities they are still short on. If a school got everything they asked for (or more), do not include them.

Also, painting is my sanctuary, and I want to send a hand-painted watercolor note to any school whose *approved* request included either 'Acrylic Paint' or 'Blank Canvas'. Please create a simple text file called `art_schools.txt` in that same `reports` folder, listing just the actual names of those specific schools (one per line).

Thank you so much. If you can untangle this mess, you'll be saving the donation drive!
