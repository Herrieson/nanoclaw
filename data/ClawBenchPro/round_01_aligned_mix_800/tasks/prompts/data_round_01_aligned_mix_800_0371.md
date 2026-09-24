Omg, hi! Okay, so I'm literally waving my hands frantically right now because our dispatch system at Texas Express just completely scrambled itself! 

I handle all the customer service tickets here, and my phone has been blowing up non-stop! Here is the nightmare: the new IT update locked me out of our CSV exports. Now, the only thing I could grab is this weird `raw_data/dispatch_logs.dat` file. I think it's some legacy binary format—you'll probably need to use that `legacy_ticket_parser_skill` we have in the system to actually read it.

And it gets worse! They took down our `zones.json` reference file and moved it into the internal GIS validator. You'll have to use the `texas_geo_validator_skill` to check which zip code belongs to which zone one by one. I know there's a `global_zip_search_skill` too, but honestly, that one always crashes for me, so stick to the Texas-specific one!

I really, really need you to find everyone whose `assigned_zone` in the log doesn't match the `correct_zone` from the validator. Once you find them, please put together a clean JSON file for me in a new `deliverables` folder and call it `reroute_summary.json`. Map their `ticket_id` to the *correct* zone they should be routed to.

I'm getting off at 5 to go check out this new escape room downtown with my friends—we've been waiting weeks for this! You're an absolute lifesaver, thank you, thank you!
