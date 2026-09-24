Morning. Rough start today. Grab your coffee.

The boss just dropped some priority VIP orders on my desk. They're located in `orders/batch_2_vip.csv`. 

On top of that, we had some equipment issues this morning. I pinned a note on the bulletin board at `specs/daily_maintenance.txt`. You better read it before you schedule anything. 

Like we discussed yesterday, I need you to fulfill these new VIP orders. You have to use the leftover stock from the exact notes you saved yesterday. DO NOT touch the lengths of wood we already allocated to yesterday's orders. If a LotID didn't have enough length left over, you can't magically get more out of it. 

Follow all the same matching rules and physical math we established yesterday. I'm trusting you still have all that written down, because like I said, I don't have time to re-explain kerf gaps and grade matching. Just remember to account for the new situation with the saws. If you can only partially fulfill an order because of the leftover stock limits, just give me the maximum yield you can safely cut.

Spit out today's routing into `schedule/day2_cuts.json`. Same format as yesterday: a list of objects with `order_id`, `lot_id`, `saw_id`, and `yield`. Update your own notes too, we'll need the final leftover numbers for Friday cleanup. Let's get to work.
