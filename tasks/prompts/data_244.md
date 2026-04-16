I need some help processing some warehouse data for a DIY e-ink display I'm building at home. I manage inventory at a manufacturing plant and I want to automate my daily log reconciliation. 

In my workspace, there is a SQLite database `inventory.db` and a directory called `scanner_logs` with today's raw text logs from the barcode scanners. There's also a `blacklist.txt` file containing codes for vendors with known labor rights violations.

Here is what needs to be done:
1. Parse all the log files in `scanner_logs`. The format is roughly `TIMESTAMP | ACTION: <IN/OUT> | PID: <product_id> | QTY: <quantity> | VENDOR: <vendor_code>`.
2. Update the `stock_quantity` for the corresponding items in `inventory.db` (table: `inventory`). An 'IN' action adds to the stock, and an 'OUT' action subtracts from it.
3. Generate a `dashboard.json` file in the workspace root. It should contain exactly two keys:
   - `"total_stock_items"`: The sum of all `stock_quantity` across all products after updates.
   - `"low_stock_alerts"`: A list of the `product_id`s for the 3 items with the lowest stock quantities after updates (ordered from lowest to highest; if tied, sort alphabetically by `product_id`).
4. We need to monitor shipments from anti-worker companies. For any 'IN' action in the logs where the vendor code matches one in `blacklist.txt`, write a line to a new file called `flagged_shipments.txt`. The format for each line should be exactly: `product_id,vendor_code,quantity`.

I prefer to keep things simple and practical, so just get the files updated and created. I don't need a tutorial.
