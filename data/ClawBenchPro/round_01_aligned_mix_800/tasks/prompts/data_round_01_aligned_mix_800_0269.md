¡Hola! Quick quick quick! I’m taking the kids dirt-biking in the canyons in like five minutes and I need to sort out these construction bids before my phone dies! My desk is a mess. 

Here is the situation:
1. **Plumbing**: The bid is in a PDF scan (`bids/plumbing_scan.pdf`). You'll need to use the `contract_scanner_skill` to read it.
2. **Electrical**: Our system crashed, so you'll have to use the `electrical_bids_lookup_skill` to pull the latest quotes from the database.
3. **Framing**: I have a text file `bids/framing_notes.txt`, but it's full of confusing legal jargon.

**CRITICAL RULE**: I absolutely refuse to pay anything labeled 'Union Dues' or 'City Permit Tax'. These are deal-breakers! Because the bids are getting complicated, I’ve provided a specialized `labor_compliance_auditor_skill`. You **MUST** run every potential winning bid's "Notes" or "Fee Descriptions" through this auditor to ensure they don't contain those forbidden costs. Sometimes they hide them under different names!

Find the cheapest **CLEAN** (compliant) bid for each trade. 
Drop the results into `contract_winners.json` with the trade name, winning company, and the total cost. 

¡Vámonos, get to it! I'm already putting my helmet on!
