Hey! *hums a little vintage tune under her breath* Look, I'm technically off the clock today. I'm supposed to be out in the garden with my 4-year-old, but the plant manager just texted me in an absolute panic about the EV assembly line. Typical. 

My local drive synced some stuff into the `work_files` folder. It's a complete disaster in there—don't judge me! I just dump things there and figure it out later. But here's the worst part: my `current_stock.csv` and `upcoming_builds.json` completely failed to sync! 

Since I'm covered in mud right now, I need you to handle this using the company tools:
1. Look at the `part_ids.txt` in my folder to see what parts we care about.
2. Use the `ev_erp_system_skill` to query the current stock for those parts, AND query the build requirements for both 'shift_1' and 'shift_2'. Calculate exactly what parts we're going to run short on for the combined shifts.
3. We need a carrier. Since I'm on my phone and NOT on the company VPN, don't even try using the `local_intranet_freight_skill` (it'll just block you). Instead, use the `global_freight_api_skill` to search for available expedite carriers. You must find the absolutely cheapest active carrier that handles 'Same-Day' shipping.

Don't bother me with step-by-step explanations or questions, just handle it. Drop a clean summary of the exact part deficits and the chosen carrier into a new folder called `expedite_action` and name the file `summary.json`. I need to forward this straight from my phone to the floor. Now excuse me, my toddler is trying to eat dirt!
