Hi... *takes a deep breath* okay. I'm trying really hard not to panic, but I really need your help before the 2 PM production meeting. 

I'm supposed to coordinate the materials for the floor, but my notes are just... well, they're a complete mess. I was trying to keep track of the Bamboo Fiber batches in `inventory_notes.txt` because we're really pushing for these new eco-friendly product lines, but things kept moving around and I was so distracted! *waves hands frantically* I'm pointing at my screen right now, but obviously you can't see that. 

Anyway, we have Order 992 in the `schedule.csv` that absolutely has to go out to Assembly today. But I completely lost track of where the Bamboo Fiber actually is right now in the facility. 

I need you to figure out exactly how much Bamboo Fiber is sitting in each location based on my notes. Once you figure that out, please write up a `transfer_order.json` in the same folder. It needs to specify the `"order_id"`, the `"material"`, the `"destination"`, and a list of `"transfers"` (each with a `"source"` and `"quantity"`). You have to move the exact total amount required for Order 992 to Assembly. You can pull from any location that currently has the material, just don't pull more than a location actually has! 

Please just make sure the math is right. If I mess up another schedule, my boss is going to flip, and I really just want to go home, cook some pho, and forget this week happened.
