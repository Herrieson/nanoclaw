Peace and blessings to you on this beautiful day. I pray this message finds you in good health and a tranquil spirit. 

I am organizing our weekend outreach, but I am afraid I am completely overwhelmed. The dear children in our youth group offered to digitize all our records, but heavens, they've scattered everything into hundreds of little files across so many folders! I just don't have the schooling to make sense of this digital maze.

Here is what they told me:
- The items we have received over the past month are stored in the `donations/` folder, divided by weeks. The files are a mix of spreadsheets and data files. However, the kids said they accidentally left some messy files in there—please **completely ignore** any files with `draft` in the name or that end in `.bak`.
- In those donation records, they used internal `item_id`s instead of names. You will need to match those IDs with their actual names using the catalog in `inventory_master/item_catalog.json`.
- They also used `status_code`s to mark the condition of the donations. Please check the guidelines folder. Make sure to use the **latest** `status_codes_v2.csv` file (please ignore any older versions) to identify which codes mean the item is usable. We absolutely cannot distribute anything where the `Usable` column is not `True`.
- The families' heartfelt requests are saved as individual text files in the `family_requests/` folder. You'll need to read through them to find their `Family ID` and exactly what they need.

Could you please help me calculate our usable inventory and figure out the distribution? 

To be perfectly fair to everyone, please allocate our stock to the families **strictly in alphabetical order of their Family ID** (e.g., F-001 gets their share before F-002). For each family, fulfill their requested items as much as our usable stock allows. If we run out of an item, just give them what we have left and move on. 

Please place the final plan in a new folder called `outreach_plan`, in a file named `final_plan.json`. 
I need two main sections in this file:
1. `"allocations"`: Showing what each family receives (organized by Family ID, then item name, then quantity). Please do not include families or items if they end up receiving zero.
2. `"shortages"`: Showing the total missing quantity across all families for each item we couldn't fully provide. (Again, exclude items if there is no shortage).

Thank you for your infinite kindness and dedication. I will keep you in my daily prayers!
