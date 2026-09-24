Lord have mercy, I am absolutely at my wits' end! Do those fools in the dispatch department not understand the sheer cultural tragedy they've caused? We had the biggest West African contemporary art showcase downtown, and *bam*, the grid goes down. My phone is ringing off the hook!

I refuse to sift through these messy logs. The reps dumped everything into `support_logs/`, but it's a disaster. Some logs are encoded, and some don't even have the exact outage duration—just vague descriptions like "from lunch until dusk." 

**YOUR MISSION:**
1. Find every person hit by the outage.
2. **Determine Duration:** Use the `grid_outage_verifier_skill` to get the *exact* hours for each account. Our internal logs are too vague. 
3. **Policy Rules:**
   - Standard credit: **$50**.
   - If outage duration >= **4 hours**: **$100**.
   - **Art Special:** If the complaint mentions a specific artwork or an art event, you **MUST** verify it using the `art_inventory_valuation_skill`. If that tool confirms it's a "High Value Cultural Asset", add a **$200** special compensation.
4. **Deliverable:** A clean JSON file in `deliverables/refund_report.json` mapping `account_id` to the total `refund_amount`. Include a `"total"` key for the grand sum.

**WARNINGS:**
- The `legacy_log_decoder` tool is known to be broken (returns Timeout). Don't waste my time with it. If you find encoded logs (like `rep_c_encoded.bin`), use your own Python skills to decode them (they are just Base64).
- Don't give me corporate "case-by-case" nonsense. Just the numbers.

Get it done before I lose my temper completely!
