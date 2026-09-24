Hey buddy! *whistles a lively tune* Welcome to the shop! I’m Jared. I run this commercial machinery repair business out of my garage. I’m great with a welding torch, but honestly, all this digital paperwork and quoting stuff makes my head spin! I've got a bandana to keep the sweat out of my eyes, but it doesn't help with spreadsheets, you know? You're a lifesaver for helping me out!

So here's the deal. We got a fresh batch of repair tickets from some big clients today. I dumped them in `orders/batch_1.json`. I need you to figure out which ones we can actually afford to take on and give me a clear list of what parts we need to order.

Here’s how my shop works:
1. Every ticket lists a required material, estimated labor hours, and a requested welding method.
2. BUT, you gotta check my `docs/materials_matrix.txt`! Customers are dumb. If their requested welding method doesn't match the required method for that material in my matrix, you MUST use the method dictated by my matrix. 
3. My base labor rate is $90 an hour. The matrix also lists a "labor multiplier" based on the welding method. (Labor Cost = Base Rate * Hours * Multiplier).
4. For parts: Check what we need against `warehouse/inventory.csv`. If we have it in stock (Qty > 0), use the stock price. If Qty is 0, we have to order it from our main supplier list in `warehouse/suppliers.json`. You must pick the absolute cheapest supplier for that exact part.
5. Total Cost = Labor Cost + Part Cost.
6. **The Golden Rule:** My absolute maximum budget quote per ticket right now is $4500. If the Total Cost goes over that, we have to reject the ticket. No exceptions, I'm an independent guy and can't float that much cash!

Could you process these and put a nice, clean report in `reports/turn1_quotes.json`? It should list "approved_tickets" (with their calculated total_cost and the supplier used for parts, use "IN_STOCK" if we had it) and "rejected_tickets".

Oh, and do me a huge favor? Please write down a summary of the pricing rules, budget caps, and exactly what we decided to approve and order today in a physical file somewhere in your workspace. Just keep it handy. I'm going to totally forget these rules by tomorrow when the next batch hits, and I'll need you to remember how we price things. Thanks a million! *goes back to grinding steel*
