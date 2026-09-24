Oh my gosh, hi! *frantically adjusts yoga mat strap and pushes up smudged glasses* It's Mai from the GreenGlow loading dock. I am literally hyperventilating right now. 

Corporate just pushed this "Enterprise Resource Optimization" update yesterday while I was at my Vinyasa retreat, and it completely nuked the human-readable inventory system! Everything is shattered into hundreds of daily digital scraps in the `archives/dock_logs` folder. To make matters worse, they stopped using plain text like "Certified Organic" and replaced them with these hideous certification codes. 

I *really* need a total weight summary of all the "Certified Organic" ingredients we actually received. But here's the nightmare:
1. You can't just trust any log. Some of our inspectors were laid off or reassigned! We can ONLY accept ingredients approved by an `Active` inspector. I think the HR folks left the registry somewhere in the `compliance` folder.
2. The certification codes are also mapped out in that `compliance` folder. Please figure out which code means "Certified Organic" and ignore the pending or rejected garbage. I only want the pure stuff!
3. The warehouse guys started logging weights in kilos (kg) and ounces (oz) just to mess with me. We strictly report in pounds (lbs). I left a sticky note about conversions in the compliance folder too. If there's no unit, assume it's already lbs.
4. Watch out, my daughter's Bat Mitzvah guest lists and catering notes got sucked into the system backup. Just ignore anything that isn't soap ingredients!

Could you please write a script to sift through this apocalyptic mess? Cross-reference the active inspectors, decode the organic status, convert the weights, and tally up the total pounds for each organic ingredient. 

Drop a single JSON file named `certified_totals.json` in the `inventory_reports` folder. Format it simply as `{"Ingredient Name": TotalWeightInLbs}` (round to 2 decimal places). I owe you a lifetime supply of shea butter if you fix this before my manager finds out! Thank you!!!
