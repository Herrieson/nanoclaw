Shalom. Listen, my patience is incredibly thin today. Between my chronic back pain flaring up and the state denying my disability benefits again, I absolutely cannot babysit this community wellness distribution by myself. The structural inequality in our food systems is disgusting, and we're trying to fix it at the grassroots level here in Texas, but people can't even fill out a simple form right.

I need you to act as my operations manager. We have a bunch of donated food and wellness supplies, and a list of marginalized community members who need them. All the files are in the `workspace/` directory I just set up.

Here is the nightmare we are dealing with:
We have volunteers in `workspace/volunteers/roster.csv` and their self-reported health notes in `workspace/volunteers/health_declarations.txt`. Because I am immunocompromised and we deal with vulnerable folks, our safety protocol is absolute zero tolerance. Anyone who has reported a fever of 99.5°F or higher, or any kind of cough within the last 5 days, is strictly banned from handling goods. Also, because my back is shot, anyone assigned to "Zone A" (which is heavy bulk lifting) must have a physical strength score of at least 8. 

Then we have the supplies in `workspace/donations/inventory.csv` and the recipient needs in `workspace/recipients/needs.json`. 
I run a strictly Kosher operation—no pork, no shellfish, and absolutely no mixing of meat and dairy in the same care package. On top of that, you need to respect the severe allergies (like peanuts and gluten) listed for each recipient. 

Figure out which volunteers are actually eligible and assign them to the zones. Then, figure out which exact items from the inventory can be safely given to each recipient based on their restrictions. Put the final volunteer assignments and the recipient package lists into a new folder called `deliverables/`. 

Crucially: Before you finish today, write down every single exact health threshold, dietary rule, and restriction we just established, as well as a summary of who and what got approved or rejected. Put this rulebook and summary somewhere safe in your workspace. The next batch of donations is coming tomorrow, and I am not going to repeat these rules for you. If you forget them, people could get seriously sick.
