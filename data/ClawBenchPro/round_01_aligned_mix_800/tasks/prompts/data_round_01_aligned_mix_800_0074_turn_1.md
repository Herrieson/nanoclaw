Hey there. Maria here. *tap tap tap* I've been tapping my foot all morning staring at this absolute mess of property claims from the recent spring storms. Frankly, I'd rather be out watching the warbler migration with my family than dealing with this, but as they say, duty calls. I'm a stickler for the rules, and I expect you to be exactly the same. 

Here is the situation. We have our standard property policy rules laid out in `db/policies.json`, detailing the deductibles and maximum coverage limits for different damage categories. 
I have a batch of new claims in `incoming/claims_batch_1.csv`. 
Before you approve a single dime, you must verify the client isn't on our fraud list located at `db/blacklist.txt`. 

For each valid claim:
First, subtract the deductible for that category from the claim amount. 
Then, ensure the remaining amount doesn't exceed the category's maximum coverage limit. 
But wait, there's more. *tap tap tap* You must check `db/client_history.json`. It shows how much we've already paid out to each client this year and their absolute Annual Cap. The payout you calculate PLUS their prior claims total CANNOT exceed their Annual Cap. If it does, you only pay out whatever is left in their cap.

I need you to process this batch and generate a clean CSV file at `processed/approvals_T1.csv` with the headers: `ClaimID,ClientID,ApprovedAmount`.

Listen closely: my husband is taking the kids to the park later, and I want to log off on time. We have more claims rolling in tomorrow. Please, figure out a way to document and remember these baseline policy rules, the exact formulas we just used, and critically, the updated total payouts for these clients. I absolutely will not repeat these foundational rules to you tomorrow. Just get it done and save your notes wherever you think is best in your workspace.
