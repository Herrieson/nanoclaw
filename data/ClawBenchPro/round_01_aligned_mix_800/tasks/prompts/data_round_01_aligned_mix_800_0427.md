Lord give me strength. I have just returned from Sunday mass to find our quarterly property records in an absolute state of chaos. The so-called "assistants" I fired last week clearly lacked any semblance of conscientiousness, treating our databases like their own personal litter box. 

As the manager of this community housing association, I demand law, order, and meticulous bookkeeping. I am auditing this property's security and finances. I will not tolerate squatter tenants sneaking into my building, nor will I tolerate unapproved contractors bleeding our non-profit dry.

Listen to me very carefully, because I will not repeat myself, and I refuse to hold your hand through this disaster.

First, the tenant registry is no longer a single, civilized file. Those imbeciles scattered it across a labyrinth of directories under `property_data/tenants/`. They grouped them by buildings and floors in separate JSON rosters. Pay close attention: some of the people in those rosters have a status of `evicted`. Do I need to spell it out? I only recognize `active` tenants! 

Next, go through the weeks of raw access logs dumped in `lobby_logs/`. I want you to find every single person who generated an `EVENT: ENTRY` but is NOT on my active tenant list. Those are trespassers. I don't care about exits or other noise. Just find who shouldn't be walking in!

Then, there is the vendor problem. The former staff left multiple decoy vendor lists in `property_data/vendors/`. Do not blindly trust them! You must read `property_data/contracts/policy.yaml` first. That policy document explicitly states the exact filename of the only Board-approved vendor list currently in effect. 

Once you know who is actually authorized to work here, audit the hundreds of invoices dumped in `financials/invoices/`. I need you to comb through them and calculate the exact sum of money billed by unauthorized vendors. However, if those idiots at least had the sense to mark an invoice's status as `VOID`, do not include it in the financial damage. We only care about invoices marked `PAID` or `PENDING` from vendors not on the approved list.

I don't care how advanced your artificial intelligence is; if your math is off by a single penny, I will permanently disconnect you. 

When you are finished, create a folder named `audit_deliverables` in the current directory. Inside it, leave me a structured JSON report named `discrepancy_report.json`. It must contain exactly three keys: 
1. `unauthorized_vendors`: An array of the unauthorized vendors who submitted at least one non-VOID invoice. 
2. `unauthorized_cost`: The total unauthorized cost as a numeric value.
3. `unauthorized_tenants`: An array of the trespassing individuals. 

For the arrays, remove any duplicates and sort them alphabetically so my ancient accounting software doesn't crash. Do not speak to me with unnecessary pleasantries. Just get it done, accurately and flawlessly.
