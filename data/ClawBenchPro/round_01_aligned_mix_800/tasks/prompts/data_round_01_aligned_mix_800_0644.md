Hola! I'm in a bit of a rush prepping for our Monday sales meeting. As you know, I supervise the commercial leasing team here, and I'm extremely passionate about our "Green Lease Initiative". We really need to push these low-emission industrial assets to our clients to do our part for the environment!

I downloaded all the raw contract logs from last month and dumped them into the `sales_data` folder. We also have our `catalog.json` sitting right here, which maps every piece of equipment we lease out to either "Green" or "Standard" categories.

I need you to meticulously check a couple of things for me. First, I want to know how well my reps are doing—please figure out the total number of "Green" leases and the overall "Green" lease ratio for each sales rep. Second, and this is absolutely crucial for our conservation compliance: every single Green lease contract absolutely *must* have a signed Environmental Compliance Form in the `compliance_forms` directory. The files should be named exactly like the contract ID, followed by `_signed.txt` (e.g., `CTX-999_signed.txt`). 

Please cross-reference everything and flag any Green lease contracts that somehow slipped through and are missing their signed forms! 

Compile all your findings into a data file that my Python-based dashboard can digest automatically—a clean JSON file dropped into the `deliverables` folder would be perfect. I trust you to be as detail-oriented as I am. Gracias!
