Hello... I hope you're having a peaceful day. 

I work in the cafeteria most days, but in my quiet time, I'm very passionate about sustainable fashion and DIY projects. I try to be very meticulous with my materials, but my inventory log has gotten slightly out of hand. 

I have a file called `inventory.log`. Could you please look through it and find the items where the status is "LOW STOCK"? 

Once you know what I need, I need you to check my local supplier database (`supplier_db.sqlite`, inside the `catalog` table). Since I care deeply about the environment, I only want to buy fabrics with an `eco_score` of 8 or higher. However, my income is quite limited, so for each fabric I need to restock, please find the single supplier that offers the lowest `price_per_yard` among those that meet the eco-score requirement.

Please write the final list into a file named `shopping_list.csv`. It should have exactly three columns: `fabric_name`, `supplier_name`, and `price_per_yard`. I'd really appreciate it if you could include a header row too.

Thank you so much for helping me keep things eco-friendly and organized.
