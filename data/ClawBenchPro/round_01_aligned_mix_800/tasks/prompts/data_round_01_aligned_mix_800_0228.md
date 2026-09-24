Oh, hi there! *pushes up glasses leaving a slight smudge* Sorry, I was just finishing my trail mix. I'm Mai. I handle all the material moving down at the loading dock for GreenGlow Cosmetics. We make really pure, natural soaps. 

Listen, I am in a bit of a bind today. My conscientiousness is not my strong suit, to be honest. I dropped my water bottle on my clipboard yesterday, and now the shipment records are completely scrambled. I shoved all the recovered digital logs into the `dock_receipts` folder, but it's a mess. 

To make matters worse, the new inventory system export (`batch_A.csv`) only shows the ingredient names and their "Batch Codes", but completely dropped their certification status! And `batch_B_scan.pdf` is just a raw scan of Tuesday's messy handwriting log.

Can you do me a massive favor? I need to know the total weight of each of the **'Certified Organic'** ingredients we just received. 
You will need to:
1. Parse the files in `dock_receipts`. You might need a tool to read that PDF scan.
2. Check the certification status for each Batch Code. You can use our internal tool `greenglow_internal_cert_skill`. We used to use the `global_cosmetics_db_skill`, but I think corporate forgot to pay the subscription bill, so maybe avoid that one if it acts up.

We absolutely cannot use any batches labeled 'Pending' or 'Rejected' – I'm super health-conscious and we don't want those chemical batches anywhere near our clean soap! Also, I think I accidentally saved my daughter's Bat Mitzvah guest list in that folder too... just ignore that. 

Could you tally up the total weights for the good organic ingredients and leave a summary report for me in the `inventory_reports` folder? Any file format is fine, I just need the ingredient names and their final combined weights. I really gotta run to my Vinyasa yoga class now, my family is waiting. Thank you so much!
