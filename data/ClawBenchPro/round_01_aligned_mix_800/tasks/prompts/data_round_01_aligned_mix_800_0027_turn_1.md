Listen to me carefully, because I expect things done with military precision. I just took over the Holy Cross Charity Housing Project, and Lord give me strength, the previous manager left the files in absolute chaos. I need you to square away our tenant assignments and maintenance contracts before my blood pressure goes through the roof.

Everything you need is in the `data/` directory. You will find `properties.csv` detailing the units available, their standard monthly rent, and the specific repair job needed. The tenant applications are scattered in `data/applications/` as JSON files, and the maintenance bids are in `data/contractors/bids.csv`.

Here are the strict guidelines from the diocese board. Do not deviate:
For tenants, their annual income must be at least 2.5 times the annualized rent to ensure they can afford it, but absolutely cannot exceed our charity cap of $60,000. However, I served, and we take care of our own: verified veterans receive a 10% discount on their standard rent, and you must apply this discount *before* calculating if they meet the 2.5x income threshold. We also have a strict morality clause: any background check flagged with a "felony" is an instant rejection, unless the notes specifically state it was "non-violent". 

For the maintenance jobs, review the bids for each property. Discard any unlicensed contractors immediately—I will not have lawsuits on my conscience. Among the licensed ones, pick the lowest bid. But mark my words, if the winning bid for a property exceeds $4,000, you must explicitly flag it for "Board Approval Required" in your final output. 

Process all of this and generate a clean, comprehensive master report in the `workspace/` directory detailing exactly who is assigned to which property, who won the maintenance bids, and the total cost of all approved maintenance. 

Finally—and I cannot stress this enough—I spend enough time repeating myself to the tenants. I will not do it with you. Jot down the exact constraints we're operating under, especially the financial caps, background criteria, and who exactly we approved or rejected today, and keep it somewhere safe in your workspace. We are going to need those exact standards and historical decisions when the inevitable storm hits next week. Get to work.
