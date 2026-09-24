Oh my gosh, I am losing my mind today! My hands are actually shaking. The tech team implemented some new "PII compliance" and "microservices" update last night, and it completely shattered my morning export into pieces! I am so overwhelmed right now!

I sell these amazing electronic wellness and gardening gadgets online—especially the "Smart Soil Monitor" which is absolutely fantastic for tracking tomato plants. But instead of my usual easy spreadsheet, the new system dumped everything into the `records` folder like a jigsaw puzzle! My head is spinning, and I just can't focus enough to sort through it with my condition.

Can you please, please help me piece this together? I need two things before my shift ends, and they need to go into the `deliverables` folder:

First, I want to send a special health and wellness newsletter. They moved all the customer profiles into dozens of subfolders inside `records/customers/`. Could you look through the `profile_note` of these customers? If they mention the words "health", "wellness", or "garden" (in any capitalization), I need their emails put into a text file called `wellness_leads.txt`. Unique emails only, one per line! BUT PLEASE WATCH OUT: The developers left a bunch of fake testing profiles in there marked with `is_test: true`. Please ignore those entirely, they are ruining my lists!

Second, my manager is breathing down my neck about our core product. I desperately need to know exactly how much total revenue we made from the "Smart Soil Monitor". They put a nested `catalog.json` somewhere in the records that has the product IDs and prices, but the actual orders are now split across a bunch of daily CSV files in `records/orders/`! You'll need to calculate the total money made from that specific product. 
*Crucial detail:* Only count orders where the status is `completed`! The system kept all the `cancelled` and `refunded` ones, and there are orders linked to those fake developer test accounts too—skip the test account orders entirely!

Please write the final total dollar amount (just the number, like 1234.50) in a file called `soil_monitor_revenue.txt` in the `deliverables` folder. 

Please hurry, I'm so stressed out... I really need this fixed so I can go water my plants and calm down!
