Hey... man, I really need a favor. I’m trying to get this small exotic food pop-up thing off the ground. I got laid off from the freight warehouse a few weeks back, and while my wife is super supportive, money is tight and with the toddler running around screaming all day, I can barely hear myself think. 

I've always loved trying weird, exotic foods, so I'm trying to import some rare ingredients. I spent all night looking up suppliers and just haphazardly copy-pasted everything into a file called `supplier_notes.txt`. It's a complete mess. I also wrote down what I actually need to buy for my first test batch in `shopping_list.txt`.

I'm really bad with computers, and every time I try to put this into a spreadsheet, my hands just start fidgeting and I mess it up. I know you're good at this stuff. Could you write a script or something to go through my notes and figure out the absolute cheapest way to get my ingredients shipped here to Wisconsin? 

For each item on my shopping list, I need you to find the cheapest supplier. The cost for a supplier is the (Item Price * Quantity I need) + their Flat Shipping Rate. 

Please just generate a clean file named `order_summary.json` in the same folder. It needs to have a list of the items, showing the "item" name, the chosen "supplier", the "cost" (which is the total cost for that item including shipping), and at the very end of the JSON, a "grand_total" for everything combined. 

Please man, this could really help my family out. I'll let you try some of the fermented shark when it arrives!
