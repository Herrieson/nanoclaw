Hey there. Kurt here. Look, I run the saws on the floor, and I like things measured twice and cut once. I've got a shop floor to run, so I need you to handle the routing and math for today's production schedule. 

All our raw lumber inventory is sitting in `warehouse/lumber_stock.csv`. The orders we need to fulfill today are in `orders/batch_1.csv`. 

Here is the deal: we only do cross-cuts here. That means the `Width` and `Thickness` of the stock lumber MUST exactly match the `Req_Width` and `Req_Thickness` of the order. You can't use a 10-inch wide board for an 8-inch wide order. We only cut down the `Length`. Also, the stock grade needs to be at least as good as the order's minimum grade (Grade A is better than Grade B). 

You also need to pick the right machine from `specs/saw_calibrations.json`. The saw obviously has to be "Operational", and the stock's Thickness must fall exactly within (inclusive) the saw's Min and Max thickness. 

Now, the tricky part—use your hands for a second, figuratively speaking. Every time a saw blade goes through a board, it grinds some wood into sawdust. We call that the "Kerf Loss". If you cut a board into multiple pieces, you lose kerf material *between* every single piece. So to get 2 pieces out of a board, the total length consumed is `Req_Length * 2 + KerfLoss * 1`. To get 3 pieces, it's `Req_Length * 3 + KerfLoss * 2`. Make sure the stock length can actually fit the pieces plus the required kerf cuts!

I need you to figure out which OrderID goes to which LotID using which SawID, and how many pieces you can yield from that Lot. We need to fulfill the exact Qty requested if possible. Generate a JSON report and save it directly to `schedule/day1_cuts.json`. It should be a list of objects containing `order_id`, `lot_id`, `saw_id`, and `yield` (the number of pieces cut). 

One last thing: I ain't repeating these rules tomorrow. I need you to write down exactly how we calculate this kerf math, which saws we have, and most importantly, an updated list of the exact lengths of stock we have left over *after* these cuts. Save this in whatever format you want in your workspace, just make sure you keep a permanent record of it so we can pick up right where we left off tomorrow. Don't double book my wood!
