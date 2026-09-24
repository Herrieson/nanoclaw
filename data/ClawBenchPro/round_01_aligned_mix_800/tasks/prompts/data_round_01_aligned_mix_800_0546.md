Hey. Listen up. I'm the Non-Retail Sales Supervisor, and my blood pressure is through the roof. The IT department completely botched our system migration last night, and now our entire Q3 inventory and sales data is a scattered, horrific nightmare. The execs need the final discrepancy audit in hours, and if I go down for this, I'm taking everyone with me.

Here is the situation. I need you to find two things: the "Ghost Stock" (things we officially sold but never actually shipped) and the total revenue loss from "Damaged Returns" that night shift ruined. 

The data is dumped into the `raw_inventory` folder. It's a disaster zone.
First, those warehouse idiots broke the export tool. Instead of one clean出库(shipment) log, there are hundreds of text fragments buried in the `warehouse_logs` subdirectories. They also have a broken barcode scanner—it jams and registers the exact same transaction ID (`tx_id`) multiple times. You cannot count the same `tx_id` twice! And don't get me started on the statuses: they logged items as `PENDING_OUT`, `MAINTENANCE`, and even put negative quantities when they screwed up. I ONLY care about status `OUT` with positive quantities. Anything else is garbage.

Second, the sales records are in the `sales` directory. It's full of junk. Half of them are drafts or cancelled orders. I only care about JSON files where the internal `status` field is exactly `"CONFIRMED"`. Add up what we actually sold. 

Third, the damaged returns. No one enters them in the system. The night shift supervisor, Mike (I think his email has 'mike.nightshift' in it), sent me an email about the broken stuff. You'll have to dig through the `emails` directory, which is full of hundreds of automated alerts. Find Mike's email with a subject containing the word "Write-off". The item IDs and quantities they broke are in there.

To calculate the financial loss for those damaged items, you need the unit prices. Look in the `pricing` directory. IT drops a new master price list CSV every few weeks. They are all mixed up. You MUST use the one with the highest version number in the filename (like `master_prices_vX.csv`). Do not use outdated prices!

Figure out the total actual shipped quantities, subtract them from the confirmed sold quantities, and whatever positive difference remains is our "Ghost Stock". 

When you have sorted out this mess, create a new directory named `audit_reports`. Inside, put a clean file named `summary.json` structured exactly like this:
`{"ghost_stock": {"ITEM-ID1": 10, "ITEM-ID2": 5}, "total_damaged_loss": 1234.5}`

I'm out of patience. Write a robust script to tear through these files, filter out the noise, and get me that JSON. Do not guess. Calculate it.
