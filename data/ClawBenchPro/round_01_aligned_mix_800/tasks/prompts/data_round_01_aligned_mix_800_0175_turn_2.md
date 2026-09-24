Jesus, it's a complete mess today. The FDA just issued a massive alert and my patience is practically zero.

Here's the deal: Anything manufactured by "CelticPharma" or "GaelicHealth" has been completely recalled. Do you hear me? Recalled. Absolute zero tolerance. 

I dumped a new batch of patient refill requests into `requests/new_refills.xml`. You need to process these requests against the running stock you established yesterday. 

Here is how you process them:
Check each request against the compliance limits we set yesterday. If a request violates those limits, or if it's for a recalled manufacturer, reject it. If it's valid and we have enough stock, approve it and deduct it from your running stock.

I need two clean files in the `requests` folder: `approved_refills.csv` and `rejected_refills.csv`. Both should just list the request IDs and the drug name. 

Update your own notes on our running stock after these approvals. Do it right, I'm not in the mood for errors.
