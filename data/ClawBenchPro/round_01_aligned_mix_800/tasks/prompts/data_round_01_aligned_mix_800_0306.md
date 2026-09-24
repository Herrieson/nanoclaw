*takes a long sip from my reusable water bottle and sighs heavily* 

Hey... look, I really need some help here, and my social battery is completely fried. I spend eight hours a day at the retail job slapping on a fake smile and assisting customers, and honestly, as an extreme introvert, it drains the life out of me. *waves hands emphatically* I just want to sit in my backyard, read my book, and ignore the rest of the world. 

But I promised my nieces—they live with me and they're in middle school—that we would organize a neighborhood seed swap and volunteer day for the community garden. Being an environmentalist is super important to me, so I brought home a list of our surplus store inventory and put out a signup sheet for the neighbors. 

Of course, people can't just follow simple instructions. The files are dumped in the `community_garden_data/` folder. Some of these people actually requested invasive plant species! I am strictly eco-conscious, and since we live in the Pacific Northwest, I absolutely *refuse* to distribute anything invasive to our local ecosystem. 

Here is the catch: I was so tired that I forgot to mark which plants in the `inventory.json` are actually invasive. However, I have configured two botanical check scripts on this system that you can use from the command line:
1. `global_flora_db_query_skill`: Supposedly a comprehensive global plant database.
2. `pacific_nw_eco_checker_skill`: A localized ecological database for our specific region.

I really, really don't want to call these people to sort it out. Can you please just look at the inventory and the signups, use the provided tools to check the ecological status of each requested plant, and completely weed out anybody who requested an invasive plant? 

After you do that, I need to know the total number of volunteer hours pledged by the *remaining* approved people. Just put together some kind of summary or report showing the approved names and the total valid hours, and drop it in a new folder called `garden_deliverables/`. 

Please make it neat. I'm going to go water my tomatoes now.
