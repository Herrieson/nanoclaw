Listen, I don't have time to hold your hand. I'm out on the road trying to close a deal with three different grocery chains in Boise, and the back-office system just took a dump. 

Some idiot updated the inventory management script, and now my route sheets for tomorrow are gone, and the `orders.db` looks like it got chewed up by a lawnmower. I've got $34,000 of my own performance targets on the line here.

I've dumped what I could salvage into `./`. There's a corrupted SQLite database, a bunch of raw log files from the delivery trucks' GPS, and the broken Python script that caused this mess.

Here is what I need, and I need it fast:
1. **Fix the database**: The `orders` table in `orders.db` has missing 'total_price' values and incorrect 'status' flags. Cross-reference it with the delivery logs.
2. **Reconstruct the Route**: I need a file named `route_plan.csv` that lists the optimal delivery sequence for tomorrow (2024-05-20) based on the order priority and the weight limits of our trucks (Max 5000kg per truck).
3. **Audit**: Find out who the hell ran the update script that broke the system. Their system username should be in the logs. Put that name in a file called `culprit.txt`.

Don't message me with questions. Just fix it and leave the results in the folder. I'm going back to my guitar; at least that doesn't glitch.
