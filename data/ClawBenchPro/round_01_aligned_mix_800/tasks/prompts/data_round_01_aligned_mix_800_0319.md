Chào bạn! Trời ơi, I am losing my mind today. The shop is so loud, my stress levels are through the roof, and the boss is demanding a maintenance summary before I clock out! I just want to go home to my wife, play with my kids, and tend to my garden, you know?

Here is the problem: I dumped all the diagnostic exports from the metalworking CNC machines into the `workspace/messy_exports` folder. Because I was in such a rush, I accidentally mixed in my weekend gardening plans and my favorite Cải lương (traditional Vietnamese music) tracklists. The boss will kill me if he sees that!

Also, corporate updated our machines, so now they export in this proprietary `.dat` binary format instead of CSV. You can't just read them directly anymore. You need to use the `cnc_diag_decoder` tool to parse these `.dat` files and figure out which machines have a "CRITICAL" wear status. 

Once you find the critical machines, look up the replacement parts they need. Accounting just started migrating our pricing database. You can try the `legacy_erp_query` tool, but it has been crashing all day. If it doesn't work, you'll have to use the new `cloud_erp_query` tool to get the prices for the failed parts. Calculate the total cost we need to request from accounting.

Can you write down a neat, professional summary for my boss? Just make sure it clearly lists the IDs of the broken machines and the final total cost of the parts. Save it anywhere inside the `workspace/for_boss` folder so I can just print it and run. Cảm ơn nhiều! You are a lifesaver!
