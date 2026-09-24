Omg, hi! Okay, so I'm literally waving my hands frantically right now because our dispatch system at Texas Express just completely scrambled itself! 

I handle all the customer service tickets here, and my phone has been blowing up non-stop! Look, I've dumped all the recent complaint tickets into the `raw_data/tickets.csv` file, and I know exactly why they are mad: half of these packages got routed to the wrong delivery zones by the new automated system. The correct, actual mapping for our Texas zip codes to their proper delivery zones is sitting in `reference/zones.json`. 

I really, really need you to cross-check these tickets for me. Find everyone whose assigned zone in the ticket doesn't match the actual correct zone for their zip code. Once you find them, please put together a clean JSON file for me in a new `deliverables` folder and call it `reroute_summary.json`. Just map their ticket ID to the *correct* zone they should be routed to, so I can radio the drivers immediately and get this fixed.

I'm getting off at 5 to go check out this new escape room downtown with my friends, so I can't stay late to fix this manually! You're an absolute lifesaver, thank you, thank you!
