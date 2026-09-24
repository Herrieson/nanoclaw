It's me again. *taps foot impatiently*. The second batch just dropped into `incoming/claims_batch_2.xml`. Yeah, IT decided to switch to XML today. Don't ask me why, I just work here and I hate it.

As you can see, a bunch of these are for the new 'avian_damage' category. I dropped the supplementary rules for bird strikes into `docs/avian_supplement.txt`. 

Do exactly what we did yesterday. Process this new XML batch. I expect you to apply the exact same foundational logic, using your notes for the standard deductibles, category caps, and the most importantly, the running client annual totals we updated yesterday. Apply the new avian rules only to the avian claims. 

Once you've calculated the approved amounts for this batch, drop the results into `processed/approvals_T2.json`. The JSON should be an array of objects with keys `ClaimID`, `ClientID`, and `ApprovedAmount`.

And again, update your internal ledger. Keep your records straight. Don't come back to me with excuses about forgetting a client's updated annual limit.
