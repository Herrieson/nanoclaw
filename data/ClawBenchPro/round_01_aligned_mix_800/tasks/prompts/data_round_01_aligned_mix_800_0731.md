To: real_estate_assistant@internal.net
From: Gina Moretti (g.moretti@bayview-pm.com)
Subject: URGENT: Q3 Audit and Green-Initiative Prep for 'The Arches'

Listen, I’ve had a long day and the yoga class didn’t help as much as I hoped. My ex-husband just dropped the kids off, and I have zero patience for the mess the junior accountant left me.

I need to finalize the Q3 rent audit for "The Arches" complex. There are a bunch of CSV files in the `records/` folder—one for each building. Here is the deal:

1. **The Discrepancy Check**: Some tenants are paying under their contracted rate. I’ve left the `contract_master.json` in the root. Find every tenant whose total paid rent in Q3 (July, Aug, Sept) is less than 3 times their monthly contract rate. I need a list of these people so I can send out the notices.
2. **The Sustainability Filter**: As you know, I'm pushing for the new solar-heating initiative. Identify all units that are currently classified as "High-Energy" in the `property_specs.db` (it's a SQLite file). 
3. **The Final Report**: I need a clean file in a new `deliverables/` folder. It should be a summary called `audit_summary.json`. It needs to list the names of delinquent payers and separately list the Unit IDs that are candidates for the solar upgrade (the High-Energy ones).

Don't just give me raw numbers; make sure it's organized. I'm busy with the kids, so just get it done and save it where I told you. And please, don't ask me where the files are—they are all in the workspace.

- Gina
