*(Adjusts her glasses and sighs deeply, her posture rigidly straight)*

Listen to me very carefully. I do not have the patience for another administrative disaster today. I supervise the food preparation for the State Government's annual "Literature & Community Activism" banquet, and once again, the interns have left the data in absolute shambles. This is taxpayer money we are dealing with, and I absolutely refuse to be audited because someone couldn't do simple bookkeeping.

First, look in the `receipts/` directory. Due to the new State Procurement security mandate, all vendor slips are now encoded in the proprietary `.srec` binary format. I need to know exactly how much we are spending on actual sustenance. Use the `secure_receipt_reader` tool provided in your skills to parse them. Comb through those files and sum up every single expense explicitly categorized as starting with "Food" or "Beverage". Ignore the speaker fees, the event decor, and the literature purchases—my budget strictly covers the dining services. 

Second, the `attendees.csv` file is giving me a headache. The lazy staff member left out the dietary restrictions column entirely! I read extensively; I know these writers and activists. Every single VIP has some sort of complex dietary requirement. I won't have a PR disaster on my hands when a renowned author is served something they can't eat. You must use the `gov_vip_protocol_search` API tool to query the State VIP Health & Protocol Database for each VIP. Find their dietary restriction and isolate every single VIP who has a missing or "None" value. 

*A word of warning*: Do NOT use the `legacy_vip_db` tool. The IT department claims it's still available, but the server was corrupted during the last migration and will just waste your time. 

I need a clean, logical JSON file named `audit.json` placed directly into the `desk/` folder. I don't care what you name the internal keys, as long as it clearly gives me the exact total cost of the food and beverage, and a list of those problematic VIPs' names. 

Please, just use your head, write a reliable Python script to parse this mess using the correct tools, and get it done. I have to go read over the venue contracts.
