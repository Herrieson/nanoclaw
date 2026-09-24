Ay Dios mío, what a weekend! A huge storm hit us on Friday, delayed the concrete trucks, and changed everyone's schedule. 

We need to update our numbers based on what actually happened. The new weekend hours are in `shifts/actual_weekend.json`. This completely replaces the planned weekend shifts from before. 

I need you to re-calculate the total payroll for the whole week using these new actual weekend hours. Make sure you apply the *exact same union rules* we agreed on before—check your notes if you need to!

Also, I went to the mercado, and inflation is killing us, compadre. Prices jumped! Check `recipes/prices_v2.csv`. Listen carefully: DO NOT change the recipe assignments you made last time. Keep everyone eating what you assigned them in the first round. I just need you to recalculate how much that *same* food plan costs now using the new prices.

Please output two new files in the `deliverables` directory:
1. `updated_payroll.csv` with the newly calculated `WorkerID` and `TotalPay`.
2. `budget_variance.txt` which should contain exactly ONE number: the difference in the total food cost (New Total Food Cost minus the Old Total Food Cost you saved last time).

Make sure you update your workspace notes with this new total payroll and the new food cost. El jefe is going to want a final report soon, and we'll need these updated figures! Órale, get to work!
