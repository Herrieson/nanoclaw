Oh, hello! I am so, so sorry to bother you, I know you must be incredibly busy. I'm trying to organize a community outreach film screening and potluck dinner for our local youth center, and I'm honestly panicking a little bit. 

I exported the RSVP list from our community portal, but the system glitched out and the file is an absolute mess! It's saved in my workspace as `raw_rsvps.txt`. The portal somehow mixed up commas, pipes, and semicolons as separators, and I am just not tech-savvy enough to fix it manually without making a mistake. I usually use my hands a lot to explain things, but since I'm typing: *gestures wildly at the messy file*. 

It is absolutely crucial that we get the dietary restrictions exactly right—I'm planning to cook a few large batch recipes and I would be devastated if I accidentally caused an allergic reaction. I'm very particular about my cooking prep!

Could you please do me a massive favor and process this file? Here is exactly what I need:
1. I only want to count the votes and dietary needs of people whose RSVP status is strictly "Yes". (Please ignore "No" or "Maybe").
2. Figure out which film got the most votes among the attendees.
3. Compile a single, neat list of all the unique dietary restrictions among the attendees. Please make sure they are all lowercase, strip any extra spaces, separate them if someone has multiple (they might be separated by commas within their field), and please completely exclude "none" or blank dietary needs.
4. Save the final results in a file called `event_summary.json` in the same folder. It needs to have two keys: `"winning_film"` (a string) and `"dietary_restrictions"` (a list of strings, alphabetically sorted).

I really appreciate your help. I just want everything to be perfect for the community. Thank you so much!
