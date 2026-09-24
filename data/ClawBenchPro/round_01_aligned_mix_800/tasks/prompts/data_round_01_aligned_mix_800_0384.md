Look, I'm juggling two toddlers right now and trying to keep our community pantry running, so I'll be blunt: my DIY Raspberry Pi scanner firmware updated overnight and completely corrupted my workflow. I don't have time to fix the scripts today. 

I built it to track volunteer hours and community requests, because tracking this stuff by hand was driving me insane. But some people who haven't passed our mandatory background checks are somehow swiping in, and it's polluting my data. I'm all for social equity and getting everyone involved, but we have strict safety protocols for a reason!

Here is the situation:
The Pi dumped everything into the `raw_logs` folder. 
The check-ins are in `checkins.log`, but because of the firmware bug, it only outputs raw RFID payloads now instead of names and hours. You'll need to use my custom `diy_rfid_decoder` tool to parse those payloads back into readable volunteer data.
Also, I accidentally deleted the local `whitelist.txt`. You will have to run the decoded volunteer names through the official background check portals. I normally use the `county_bg_check`, but if their servers are acting up again, use the `federal_npo_bg_check`.

Here's what I need you to do:
First, decode the logs and cross-reference every volunteer's name with the background check tools. I need to know *exactly* who the unapproved/denied people are so I can have a direct conversation with them. 
Second, calculate the total valid hours our APPROVED volunteers actually worked. I need that number for a non-profit grant report.
Third, scan the community requests file (`needs.json`). I need you to pull out anything flagged as urgent—especially items for young kids or babies. I have a 4-year-old and a baby myself, so I know how critical those supplies are.

Put all of this into a clear, readable report and drop it in the `deliverables` folder. I don't care what you name the file or how you format it, just make it easy for me to read before my board meeting in an hour. Don't touch my original files, just give me the answers.
