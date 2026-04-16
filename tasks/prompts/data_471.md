Oye! *aggressively waves hands* Listen to me, I don't have time to hold your hand through this. I am literally humming to keep myself from screaming right now, okay?! I make $96k a year handling specialty foods, not dealing with broken 1990s IT systems! 

I am hosting a huge party tonight—making a killer paella and dancing until 3 AM—but my absolute idiot of a manager left me with a completely trashed POS system export, and the shelves are empty. ¡Qué desastre!

In my workspace, there is a folder called `pos_data`. It is full of disgusting `.log` files from the registers. I need you to comb through ALL of them. Find every single item where the action is exactly `SOLD_OUT`. 

Once you have the item codes, I need you to look them up in `catalog.db` (it's an SQLite database right there in the workspace). Find out the item name and the supplier email.

Then, you are going to create a file called `urgent_orders.csv` directly in the root of the workspace. 
It MUST have these exact columns: `ItemCode`, `ItemName`, `SupplierEmail`, `OrderQuantity`.
For `OrderQuantity`, just put `50` for every single thing. I don't care, 50 is a safe number. 
Oh, and if an item sold out like five times today, ONLY PUT IT IN THE CSV ONCE! I don't want to spam the suppliers and look stupid.

Don't ask me questions. Just fix it so I can go prep my kitchen. ¡Rápido!
