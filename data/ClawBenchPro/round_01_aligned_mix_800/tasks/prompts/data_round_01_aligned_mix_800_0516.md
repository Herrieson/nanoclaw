*pauses, letting out a heavy sigh, rubbing her temples as she stares at a blinking terminal screen* 

Oh, goodness, hello! I am so incredibly relieved you're here. Between running the optometry clinic and trying to manage this community sustainability drive, my head is absolutely spinning, and our IT system just had a total meltdown!

We held an eyewear recycling event—collecting old glasses to either refurbish or scrap for materials. It’s a wonderful initiative, but the server crashed and the recovery script just vomited everything into a deeply nested nightmare under the `data/records/` directory. There are hundreds of files scattered across different dates! 

To make matters worse, we ran several test drives and beta-events before the real deal. For the board meeting, I *only* need the statistics from the official event, which means the file's internal data must have the `event_code` set exactly to `"OPT-2023-MAIN"`. Please ignore any other events or test files.

Liability is a huge issue for us. We can *only* accept processing data from our officially registered, active volunteers. The master list of volunteers (mapping their IDs to their real names) is in `data/registry/volunteers.json`. BUT—and this is a massive 'but'—several volunteers lost their badges or had them revoked! You absolutely must check `data/registry/revoked_ids.txt`. If a volunteer's ID is in that text file, they are considered inactive, and we cannot count any items they processed!

The donation records themselves... well, let's just say data entry was not strictly enforced. The condition strings are a complete disaster. People wrote in all caps, added weird spaces, or just typed random notes. Here is my rule of thumb:
- If the condition string contains the word `"usable"` or `"good"` (case-insensitive), count it as **usable**.
- If the condition string contains the word `"scrap"` or `"broken"` (case-insensitive), count it as **scrap**.
- If it contains none of those, just ignore the item entirely.

Could you please dig through this wasteland, cross-reference everything, and compile a neat little file called `final_report.json`? Please place it inside the `deliverables` folder. I need it to have exactly three keys:
1. `usable_count`: The total integer count of valid usable items.
2. `scrap_count`: The total integer count of valid scrap items.
3. `verified_volunteers`: A list of the *Real Names* (not IDs!) of the active, verified volunteers who actually processed at least one valid item in the main event. Please sort this list of names alphabetically!

Thank you so much! I really need this ready for the community board meeting tonight, and you are my only hope!
