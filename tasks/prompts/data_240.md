Listen to me, I am having absolute heart palpitations right now. We are a week away from the "Geek Week" promotional event across our retail branches, and our main ERP system has completely crashed! I am managing operations completely blind! This is worse than navigating an asteroid field without a nav-computer!

I managed to dump the current central warehouse stock, the baseline store inventory from last week, and a bunch of messy daily sales logs from the individual point-of-sale systems. 

Here is what I desperately need you to do before I lose my mind. I need a final file named `requisitions.csv` in the current directory.
The file must contain exactly these columns: `StoreID,SKU,Title,OrderQty`.

Our priority is strictly the `Sci-Fi` and `Fantasy` genres. Ignore everything else—if we run out of cookbooks, I don't care, but if we have a red-shirt situation with our science fiction stock, heads will roll!

For every Sci-Fi and Fantasy book, I want the stock at each store brought back up to exactly **20 units**. 
You must calculate the *current* store stock by taking the baseline inventory and subtracting the sales from the logs.
If a store's current stock for a Sci-Fi or Fantasy item is less than 20, we need to order the difference.

However, the central warehouse is also running low on some titles. If the total requested quantity for a specific SKU across all stores exceeds what we have in the warehouse, you must allocate the available warehouse stock to the stores strictly in alphabetical order of their `StoreID` until the warehouse stock for that SKU is zero. Do not order more than the warehouse can supply!

The data is in the `inventory_data` directory. 
- `warehouse.csv` has the central stock.
- `baseline_inventory.json` has the stock at each store before the sales.
- `sales/` directory has CSVs of what was sold over the last few days.

Please, use your terminal, write whatever scripts you need, just give me that `requisitions.csv` file formatted perfectly! May the Force be with us.
