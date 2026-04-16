Hola. I need your assistance with a critical project for my leasing firm. We rent out commercial and industrial assets, but I am deeply concerned about our ecological footprint. I'm trying to convince my management to adopt a progressive Green Leasing Initiative to phase out high-emission equipment. We must protect our natural environment, and it starts with meticulous accountability.

I've been gathering data from our internal systems. In the current working directory, you will find our lease portfolio export `portfolio.db`. I also downloaded the relevant emission factors into `epa_emissions.json`.

Your task is to calculate the total carbon footprint for all *active* leases. The footprint for a single lease is calculated as: `Quantity` * `Duration` (in months) * `Emission Factor`. 
Please note that the equipment names in our database might be a bit messy regarding capitalization, so please match them carefully with the EPA data (treat them case-insensitively, but output them in Title Case).

I need two precise deliverables from you in this directory:
1. A perfectly formatted CSV file named `green_initiative_report.csv` with exactly two columns: `Equipment_Type` and `Total_Footprint`. It must be aggregated by equipment type and sorted from highest footprint to lowest.
2. A plain text file named `proposal.txt` containing strictly the name of the single worst polluting equipment type (the one with the highest total footprint) so I can highlight it in my executive summary.

Por favor, be extremely detail-oriented. Our conservation efforts depend on getting these numbers absolutely right. Gracias.
