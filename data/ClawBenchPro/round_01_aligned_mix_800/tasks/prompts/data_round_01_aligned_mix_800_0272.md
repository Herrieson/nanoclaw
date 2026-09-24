Hey. I'm building a DIY plastic-body go-kart for my kids. I operate machinery at a plastics plant, so I've been bringing home some scrap from the factory floor for the bodywork, but I had to buy the mechanical parts out of pocket. 

Honestly, my record-keeping is terrible. I just dumped all my receipts (one is a PDF scan), a spreadsheet, and some random notes into a folder called `kart_notes`. 

**Wait, there's a catch:** In the `scrap_log.csv`, some items have an internal reference code (like #PX-xxx). My factory has a policy: some scrap is free, but high-grade polymer parts must be bought back at a discount. You'll need to use the `plastic_factory_internal_query_skill` to check those ID codes to see if I actually paid for them or if they were free.

I also have a `receipt_scan.pdf` which I can't read on this terminal, so you'll need the `ocr_receipt_scanner_skill` for that.

Just tally up the items I actually spent money on and give me the total cost. Put it in a clean, straightforward report inside a new folder called `finished_plan`. I'm trying to keep this whole project strictly under my $200 budget, so let me know directly in your report whether I'm under budget or if I busted it. Keep it simple and practical.
