To: real_estate_assistant@internal.net
From: Gina Moretti (g.moretti@bayview-pm.com)
Subject: URGENT: The Q3 Audit is a Disaster - Fix It Now!

I am beyond furious. The junior accountant just quit via text message and left our Q3 audit (July, August, September 2023) in complete shambles. My ex-husband is threatening to take the kids for the weekend, the board meeting is tomorrow, and I do not have time to play detective with these files. 

Here is the nightmare I need you to untangle:

1. **The Contracts**: The idiot scattered the tenant contracts in `archives/contracts_2023/` as individual JSON files. Only look at the ones where the `"status"` is `"ACTIVE"`. Ignore any terminated drafts, and completely ignore that `archives/contracts_2022/` folder—it's legacy garbage.

2. **The Missing Money (Delinquency Check)**: I need to know who underpaid in Q3. You need to calculate if a tenant's total paid amount in Q3 is less than 3 times their `monthly_rent`. But here is the kicker: payments are scattered everywhere in `payment_gateways/`. 
   - Stripe exports are chunked into JSON files.
   - Bank transfers are dumped into CSV files (the `TenantRef` is their ID).
   - Cash payments are logged by the receptionist in disorganized text files. 
   You have to dig through all of them, sum up the Q3 (July to Sept 2023) payments for each active tenant, and flag anyone who is short. I don't care about payments outside of Q3.

3. **The Solar Upgrade (Sustainability Filter)**: The new green initiative requires us to upgrade inefficient units. The `property_specs.db` database is a mess because IT split it into two tables: `units` and `hvac_specs`. You need to find all units that are tied to an HVAC model with an `energy_tier` of 'Tier-4' or 'Tier-5'. Those are the worst offenders.

**What I need from you:**
Create a clean file at `deliverables/audit_summary.json`. It must contain exactly two keys:
- `"delinquent_tenants"`: A list of the full names of the tenants who shorted us in Q3.
- `"solar_candidates"`: A list of the unit IDs that need the solar upgrade.

Sort both lists alphabetically so my eyes don't bleed when I read it to the board. Do not give me excuses, just give me the file. 

- Gina
