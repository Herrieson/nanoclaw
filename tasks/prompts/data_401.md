Hola. I am completely swamped today. I'm juggling the kids' schedules and trying to finalize the material orders for the new residential build before my site visit this afternoon. I believe in self-reliance, so I expect you to figure out the details of what I need done without me holding your hand.

I was sketching out the floor plan last night and jotted down the room measurements in `project_dimensions.txt`. I also had my assistant dump the recent quotes from our vendors into `suppliers_raw.csv`. 

Here is what I need you to do:
1. Figure out the total square footage of the project from my notes.
2. Go through the supplier quotes. I need the cheapest supplier for three specific materials: **Concrete**, **Lumber**, and **Steel**. 
   - Obviously, we can only buy from suppliers who actually have the material in stock. 
   - Some quotes are from my contacts back in Mexico, so they are in MXN. Use an exchange rate of 1 USD = 20 MXN for your comparisons. All final prices must be in USD.
3. Calculate the estimated total material cost for the project. The formula I use is: Total Cost = Total Square Footage * (Cheapest Concrete Price + Cheapest Lumber Price + Cheapest Steel Price).

Generate a report named `final_estimate.txt` in the current workspace. It needs to look professional. Make sure it explicitly contains:
- The total square footage.
- The name of the selected supplier for Concrete, Lumber, and Steel.
- The total estimated material cost in USD.

I don't have time to check your math, so make sure it's accurate. Gracias.
