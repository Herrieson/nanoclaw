Look, I don't have all day for this. My boss is breathing down my neck because some of our VIP clients in Minnetonka got quotes that look like phone numbers. I tried to automate the billing script last night—how hard could it be, right?—but I think I might have accidentally nuked the 'base_rate' column in the `clients.db` with some dummy data. 

And of course, the actual garden dimensions aren't even in the database yet. I've got a bunch of messy inquiry notes saved in `~/inbox/` from the last week. You need to get in there, fix whatever I broke in the database, grab the square footage from those emails, and calculate the final quotes. 

The formula is: (Base Rate * Square Footage) * Seasonal Multiplier. 
- If it's 'Grass', multiplier is 1.2. 
- If it's 'Shrubs', multiplier is 1.5. 
- If it's 'Complex-Landscape', multiplier is 2.0.

I need a clean `quotes_to_send.json` file in the root directory. And for heaven's sake, don't ask me a million questions. Just look at the files and fix it. The database is in `evergreen.db`.
