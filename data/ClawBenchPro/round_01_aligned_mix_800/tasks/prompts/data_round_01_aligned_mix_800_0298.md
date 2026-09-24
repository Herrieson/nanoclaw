Hi there! *waves hands animatedly* 

As I was just telling my yoga instructor this morning, hosting these culturally diverse dinner parties is becoming a bit of a headache. I love exploring new cuisines, especially blending my Irish roots with something fresh, but the vendors are driving me crazy! 

Despite my day job as a financial analyst, I just don't have the mental energy to manually forecast the budget for next weekend's tasting event. The quotes are in the `quotes` directory. However, things have gotten complicated:
1. The **Seafood Invoice** is now a PDF (`seafood_invoice.pdf`). You'll need to use the `pdf_data_extractor` skill to read it.
2. For the **Wine list** (`wine_list.json`), some "base_price" data is missing because of a system glitch. You MUST use the `global_inflation_lookup_skill` to retrieve the official base prices and current inflation alerts for those items.
3. **Currency & Fees**: My Irish bank's FX API is acting up. I've provided two exchange rate tools. One might be down, so you'll have to find the one that works. The fixed rule remains: if an item has a '*' flag, add a 20% premium service fee to its final USD price.

I need the absolute total final cost in USD. Also, flag the names of any ingredients/wines where the current price has spiked by **strictly more than 15%** compared to the base price you found.

Put your final report in a clean JSON format named `dinner_budget.json` in the `financial_forecast` folder. I trust your analytical skills!
