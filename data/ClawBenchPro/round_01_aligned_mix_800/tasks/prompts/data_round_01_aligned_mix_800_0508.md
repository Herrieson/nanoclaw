Listen to me carefully, because my heart is pounding and I feel like I'm going to throw up. Tomorrow is the federal compliance audit, and our IT department just spectacularly botched a database migration. The main system is completely fried. All we have is a raw, fragmented dump in the `legacy_records` directory. 

I need you to cross-reference every single insurance claim against our policy master data and find the fraudulent or invalid ones. We cannot afford to pay out on bad claims, or we will be shut down.

Here is the nightmare you're walking into:
The policy and claim records are scattered across dozens of nested subfolders in `legacy_records`. The IT guys also dumped all the server backups in there, so the place is swarming with `.bak`, `.tmp`, and `.corrupted` files. Ignore them entirely! **Only trust files ending in `.json` and `.csv`.**

To make matters worse, the schema got completely mangled during the crash:
1. In the claim files, the policy ID is now called `policy_reference`, the incident date is `date_of_loss`, and the requested amount is just `amount`.
2. God, some field agents even typed dollar signs (`$`) and commas (`,`) directly into the `amount` fields. You have to clean that up and turn it into real numbers!
3. If a claim's `claim_status` is `WITHDRAWN`, ignore it. The client already backed out. We only care about pending ones (or ones missing the status completely).

Your job is to find claims that violate ANY of these coverage rules:
- The claim's `date_of_loss` miraculously happened *before* the policy's `active_date`.
- The claim's cleaned `amount` exceeds the policy's `limit`.
- The policy's `status` is NOT `ACTIVE` (e.g., `CANCELLED` or `EXPIRED`). Any claim filed against a non-active policy is automatically invalid.
- The claim references a policy ID that simply doesn't exist in our policy data.

I don't have time to review a messy spreadsheet. Write a script to crawl through this wasteland, apply the rules, and output a clean, flat JSON array containing *only* the string `claim_id`s of the invalid or suspicious claims. 

Save it exactly here: `deliverables/suspicious_claims.json`. Please, no formatting errors, no missed files. My entire career is riding on this.
