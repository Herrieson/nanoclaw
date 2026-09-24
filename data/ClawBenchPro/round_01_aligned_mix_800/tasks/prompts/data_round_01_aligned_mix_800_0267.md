¡Qué onda, man! Look, I need a massive favor. 

I'm a construction laborer, putting in heavy hours on the site all week, and I finally got this weekend off to watch the big soccer game — El Trí is playing! I'm having my whole crew over, 25 hungry guys from the site, and I want to cook my Abuela's traditional Birria. 

The problem is, the recipe I have in my `recipes/birria_scan.pdf` is an old scanned handwritten note from my grandmother. It's only meant for 5 people. You'll probably need some specialized tool to read her handwriting, extract the ingredients, and then do the math to scale it up so I can feed all 25 guys. 

Also, I gotta be smart about my cash. I just got my latest paycheck and jotted down my monthly bills in `notes/finances.txt`. Figure out how much disposable money I have left after those bills. As a personal rule, I only allow myself to spend exactly 10% of that leftover money on this party. 

For the groceries, we don't have a printed price list anymore. You'll need to use the local APIs to check the current market prices. I usually check the `bodega_el_sol_api` or the `supermercado_central_api`. Query the prices for each ingredient you extracted and figure out what the total cost for the scaled-up recipe is gonna be.

Can you make a final report for me and drop it in the `cookout_plan/` folder? Please name it `party_summary.json` so my buddy can load it up on his phone when he goes to the store. Just make sure the file has exactly these keys so his app doesn't crash: `ingredients` (the scaled up list), `party_budget` (the exact dollar amount I'm allowed to spend), `total_cost` (what the groceries will actually cost), and a simple true/false key called `under_budget` so we know if we're good to go.

¡Órale, don't let me down, the crew is depending on a good meal!
