Howdy! Heavens to Betsy, I am in a real bind today and could use a helping hand. 

Being a federal officer up here usually means keeping things strictly by the book, but in my off-hours, I'm organizing our precinct's first cross-cultural community food drive and festival right here on federal grounds. I just love trying new cuisines!

But we've got a situation. The gate guards handed me a secure scanned file of every license plate that drove onto the grounds this morning: `docs/gate_scanned_log.enc`. It's encrypted for precinct security, so you'll need to use the `secure_document_viewer_skill` to read the actual plate numbers.

Also, my official vendor list in `docs/registered_vendors.csv` only has the names of the folks who signed up. I don't have their license plates or their cuisine types written down anymore—the database sync failed! You'll have to use our `federal_vehicle_query_skill` to look up each license plate from the logs to see if they are a "Registered Vendor" and what they're cooking.

As a sworn officer, I absolutely have to know if any uninvited vehicles (plates not associated with our registered vendors) slipped past the perimeter. And as the festival organizer, I need a clean tally of the different cuisine types our approved vendors are serving.

Could you be a dear and rustle up a JSON report for me? 
1. Identify which license plates in the gate log are **not** registered vendors (unauthorized).
2. Count how many approved vendors we have for each specific cuisine type.
3. Save the result as `festival_report.json` in the `deliverables` folder.

I'd be mighty obliged if you could get this sorted out! 
*Note: Don't bother with the National Registry API; it's been down for maintenance all morning. Use our local precinct tools.*
