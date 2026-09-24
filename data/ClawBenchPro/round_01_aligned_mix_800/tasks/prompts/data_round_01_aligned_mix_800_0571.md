Omg, hi! Okay, so I'm literally waving my hands frantically right now because our dispatch system at Texas Express just completely self-destructed after the new "AI routing microservice" update!

My phone is blowing up non-stop! Half of our packages got routed to the wrong delivery zones, and people are furious. I need your help to find out exactly which tickets are affected. But it's an absolute disaster right now:

1. **The Zone Rules are Shattered**: The neat `zones.json` we used to have? Gone. The new system splattered the routing rules across dozens of files in `config_server/zones_sync/`. Worse, it mixed up our current rules with old deprecated ones and rules for other states. You'll have to dig through them and piece together the active mapping. Look for the metadata—we ONLY care about mappings where the `region` is `"TEXAS_CORE"` and the `status` is `"ACTIVE"`. Ignore everything else!
2. **Missing Zip Codes**: Our new ticketing system decided to be "minimalist". If you look in the `customer_support/tickets/` folders (yes, there are multiple, and they dump in both CSV and JSON formats depending on the server), the tickets only show the `ticket_id`, `package_id`, and the wrong `assigned_zone`. They stripped out the customer zip codes!
3. **The Warehouse Logs**: To find where a package was *actually* supposed to go, you'll have to scrape the raw logs in `warehouse_scans/`. There are hundreds of files nested in date folders there. You'll need to match the `package_id` from the ticket to find its `destination_zip`.

Once you link the ticket to the package, find its zip code, and check that against the *active* Texas Core mapping. If the `assigned_zone` on the ticket does NOT match the *correct* zone for that zip code, I need it flagged! 

Please put together a clean JSON file for me in a new `deliverables` folder and call it `reroute_summary.json`. Just map the mismatched `ticket_id` to the *correct* zone they should be routed to, so I can radio the drivers immediately. 

I'm getting off at 5 to go check out this new escape room downtown with my friends, so I can't stay late to fix this mess. I left some hints, but you'll have to write a script to sift through the noise. You're an absolute lifesaver, thank you, thank you!
