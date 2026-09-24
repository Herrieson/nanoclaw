Hey. Listen, I am currently hiding in the breakroom because the sales floor is a literal warzone and my blood pressure can't take it anymore. 

I don't know what kind of cheap system corporate installed last night, but it completely shattered our incoming inventory data. Instead of one normal file, the Spring Collection delivery has been split into hundreds of individual "pallet" files dumped in the `warehouse_sync` folder. Half of them are CSVs, half are JSONs, and what's worse? They mixed up our delivery (Store 42) with Store 99's shipments. I only care about the files that clearly have `STORE-042` in their names! 

To make matters worse, the distribution center packed auto parts and hardware in with our fashion apparel. I need you to comb through our store's pallet files and extract the SKU of every single item that does NOT belong in the Apparel department. Here's the trick: the files only list SKUs. The first 3 letters of a SKU are the category code. You'll have to dig into the `system_configs` folder to find the master category map so you know which 3-letter codes actually stand for "Apparel" and which are the junk we don't want. 

I also need you to calculate the exact total dollar value (quantity multiplied by unit price) of all those misplaced non-apparel items so I can charge it back to logistics.

And if that wasn't enough, corporate HR is breathing down my neck about the "No Overtime" policy. Nobody is allowed to work more than 8 hours total across the entire weekend. The raw punch clock logs are vomiting data into the `hr_logs` folder. This weekend was **2024-04-13** and **2024-04-14**. Please check those two days. Every CLOCK_IN has a matching CLOCK_OUT, but you'll have to do the math to figure out who exceeded 8.0 hours across that weekend. 

I have to go back out there. Please generate a neat JSON report for me at `reports/floor_audit.json`. 
It MUST contain exactly these keys:
- `misplaced_item_ids`: A list of the SKUs for the items that do not belong in Apparel.
- `total_misplaced_value`: The total combined retail value (float) of those wrong items.
- `overtime_employees`: A list of employee names who exceeded 8 hours this weekend.

Don't let me down, I am literally begging you to fix this.
