*¡Dios mío!* I do not have the time or the patience for this level of incompetence today. As I sit here, massaging my temples and adjusting my glasses for the hundredth time, I am reminded of Alexander Pope: "A little learning is a dang'rous thing." And my teaching staff has proven this yet again. 

I asked them for their departmental literature circle requests. Simple, right? No. They sent me a chaotic dumping ground of text files. I oversee the entire educational standard of this district, and I am reduced to manually tallying up book orders? Absolutely not. You are going to fix this.

In my workspace, there is a directory called `./`. Inside, you will find:
1. A `requests/` folder containing the teachers' rambling text files. 
2. A `budget.csv` file detailing exactly how much money each grade level is allowed to spend.
3. A `catalog.json` file containing the approved books and their unit prices.

Here is what you must do, and I expect it done without error:
Calculate the total cost of the books requested for each grade. 
If a grade's total request cost exceeds their allocated budget, I want their ENTIRE grade's request thrown out. Rejected. They get nothing until they learn to follow instructions. 
If a grade is within or perfectly on budget, their books are approved.

You must generate a final, pristine JSON file named `final_order.json` directly inside the `./` directory. 
It must have exactly this structure:
