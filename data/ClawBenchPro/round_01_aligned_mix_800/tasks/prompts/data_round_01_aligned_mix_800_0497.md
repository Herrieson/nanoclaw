Heavens to Betsy, these middle schoolers and this new "digital learning" system are driving me up the wall! I'm trying to prep for my PTA science presentation, and my digital workspace is an absolute disaster zone. We started a school garden to appreciate our local flora, but getting these kids to follow instructions is like herding cats.

First off, they submitted their plant observations every which way. My iPad synced some files, my USB drive dumped others, and some kids just emailed me text notes. It's all scattered somewhere in the `student_submissions` directory. You'll find CSVs, JSONs, and even plain text files formatted like `Student: Name | Plant: Name | Growth: 2.5`. I don't care how you parse it, just comb through all of them!

Second, you need to know who is actually in my class. The admin office dumped the roster in the `admin_records` folder (look for the 2023 CSV), but beware! Half of those kids transferred out. **Only count the ones whose status is 'enrolled'**. If a log belongs to a kid who dropped out, or some random kid from another class who uploaded to the wrong folder, ignore their data completely!

Third, the school district just updated the native plant definitions. There are a bunch of old files in the `reference_materials` folder. Do NOT use the old ones! You need to open them and find the JSON guide that specifically has `"status": "official_2023"` inside it. I only care about the growth of our beautiful **native** plants according to that specific official guide. Ignore the invasive weeds!

Here is what I need before I lose my temper:
1. Figure out exactly which **currently enrolled** kids flat-out skipped the assignment. (If they submitted *any* log at all, even a weed or a zero-growth note, they tried. I only want the names of enrolled kids who turned in absolutely NOTHING).
2. Tally up the total growth (in inches) of all the **native** plants submitted by my **currently enrolled** kids.

Create a brand new folder called `pta_report`. Inside it, put a clean JSON file named `summary.json`. It needs exactly two keys: `missing_students` (an alphabetical list of the slackers) and `total_native_growth` (the total inches, rounded to exactly 2 decimal places). Don't beat around the bush, just get it done!
