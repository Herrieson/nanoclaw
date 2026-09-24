Hey there! *adjusts glasses* I just finished my morning yoga and noticed the warehouse is a total disaster. I always try to keep things healthy and organized, but my paperwork is a mess! The delivery logs for the last two weeks are in the `inventory` folder. 

I need you to figure out how many full batches of our 'Yoga Glow' soap we can make based on the recipe in the `recipes/yoga_glow_v1.json` file. 

But listen carefully, we are super strict about what goes into our organic products:
1. Do NOT count any ingredients from vendors listed as 'Red Zone' in the `vendors/status.txt` file. 
2. Any 'Essential Oil' (like Lavender Oil) must have a purity of at least 95%.

Please give me a report named `batch_report_wk2.txt` in the main folder showing the total usable quantity of each ingredient we have right now, and the maximum number of full batches we can make. 

Assume we *actually make* those maximum batches today, and assume we always use up the oldest stuff first (First-Expire-First-Out) when making them. 

Oh, and please write down these purity rules, the red zone vendors, and exactly how much usable stock of each lot we have left over *after* making those batches! Just save it somewhere safe in the workspace you'll remember. I always forget this stuff and we'll definitely need it when the new truck arrives. Thanks!
