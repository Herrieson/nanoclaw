Man, nightmare fuel! *nervously adjusts bandana* I'm stressing out here. Apex Metals just issued a massive recall. The government goons are forcing them to pull parts, which means more headaches for honest, hard-working guys like us! 

I put the recall notice in `inbox/recall.txt`. It affects some of the parts we *just* priced out yesterday. Also, the phone keeps ringing, and we got a second batch of repair tickets in `orders/batch_2.json`. 

Here is what I need you to do, buddy:
First, take a look at the approved tickets from yesterday. If any of them relied on ordering a part from a supplier that is now recalled, we can't use that supplier anymore! You'll have to find the next cheapest supplier for that part. 
Second, re-calculate the costs for yesterday's affected tickets. If switching suppliers pushes them over our budget cap... well, we gotta reject them now. 
Third, process the new tickets in `batch_2`. 

You remember all my pricing rules, multipliers, and that strict budget cap we set yesterday, right? I'm trusting you to use those exact same rules because I didn't write them down anywhere. 

Please give me an updated, final report in `reports/combined_quotes.json`. It needs to include ALL approved tickets from both batches (after fixing the recall mess) and ALL rejected tickets from both batches. Keep your own notes updated too, we're not done with these tickets yet! Thanks man, I owe you a beer! *whistles a nervous, fast-paced tune*
