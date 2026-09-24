Ugh! *Throws hands up in the air frantically* You have NO idea how much of a disaster today has been! I am *literally* shaking right now. I just want to go home and cook or literally do *anything* else. 

*Hmm-hmm-hmmmm*—sorry, I hum when I'm stressed. Okay, look at me. I need you to fix this before I completely lose my mind. I'm trying to close up this specialty food store. Today is **Friday, November 17th, 2023**, and I have been here since 6 AM! To make matters worse, Chad—my completely useless, brain-dead coworker—was on the register for half my shift while I was restocking.

Our new POS system is a nightmare. Instead of one normal file, it dumps every single transaction into individual receipts in the `pos_dumps` folder. There are weeks of data in there! I only care about **today's** transactions. 

Here is what I need you to do. Put a file in the `reports` folder and name it `manager_report.json`. Inside that file, I need three things:

1. `"total_revenue"`: The total amount of money we actually collected *today* from all cashiers. I need this to balance this damn register.
2. `"chad_errors"`: A list of the **Item Names** (not the ID codes!) that Chad charged the wrong price for *today*. The official current prices are buried somewhere in `system_data/inventory/`. You'll have to find his employee ID in the HR records first to track his transactions. Honestly, I'm going to get him fired.
3. `"can_cook_tonight"`: True or false. I am hosting a dinner party tonight. I saved my favorite traditional recipe in my personal desktop folder (`elena_desktop/recipes/valencian_paella.json`). You need to check the morning stock for *today* (also in the inventory system), subtract all the quantities we sold *today* across the whole store, and tell me if the remaining stock is enough to make that exact recipe!

Do it NOW! I don't have all day! Find the clues in the directories, figure out the codes, and get me that final report!
