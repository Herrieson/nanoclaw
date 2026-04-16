Hey. I'm trying to get my lumber sorted for a new cabinet build this weekend. Look, I work with my hands, sawing and routing—I don't have the patience to sit here messing with spreadsheets all night. 

Over the past few months, I've kept track of my wood stock in a bunch of different files because I keep changing how I do it. They are all sitting in my `inventory` folder. I also have a script a buddy wrote for me called `calculator.py` in the `scripts` folder. It's supposed to look at my inventory and my `project_cutlist.csv` and tell me what extra wood I need to go buy.

Problem is, the script only takes ONE clean CSV file as the inventory input, and it needs the columns to be exactly: `Species,Thickness_in,Width_in,Length_in,Qty`. 

I need you to dig into that `inventory` folder, take all my scattered records, and combine them into a single `clean_inventory.csv` file right here in my main folder. Then, run that `calculator.py` script using the new clean file and my cutlist so it spits out my `purchase_order.txt`. 

Just get it done so I can hit the lumber yard tomorrow morning.
