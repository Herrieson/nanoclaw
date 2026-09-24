Listen, I'm stuck on a radio tower in a storm and the terminal link is failing. The community center network rebuild is tomorrow (Saturday), and the "volunteer coordinator" just dumped a massive heap of digital garbage into the `dump_site` directory. 

I need the final list of personnel for the Saturday "Core Rack" shift. Only those with "FiberOptic" or "Cat6" certifications are allowed to touch the hardware. The certification records are a mess—some are in legacy JSON fragments, others are in old text logs. You'll need to crawl through the `archives` and `registry` subdirectories to piece together the current certification status. Look for the most recent timestamps or "v2" markers where data conflicts.

The sign-up data is even worse. It's scattered across hundreds of tiny `log_*.txt` files in the `raw_transmissions` folder. Many are just sensor noise or corrupted packets. You need to extract names and "Hours_Offered" from anything that looks like a valid record. Ignore entries with negative hours, non-numeric noise, or "NULL" values. 

I need you to:
1. Identify every unique individual who holds EITHER "FiberOptic" OR "Cat6" based on the fragments.
2. Calculate the total VALID (positive, numeric) hours only those qualified individuals have offered across all transmission logs.
3. Save the final roster (alphabetical names and their individual total hours) and the grand total of hours into a file named `rack_shift_manifest.txt` inside a new folder called `operational_plan`.

The clock is ticking. If the rack isn't wired by Sunday, the whole sector stays dark.
