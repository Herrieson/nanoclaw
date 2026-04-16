Hello there! *waves hands enthusiastically* 

I hope you're having a blessed day. I'm currently on a bit of a sabbatical from my middle school—taking some quiet time to sketch and tend to my garden—but I'm still overseeing our parish and school's joint charity art auction. It's a wonderful cause, teaching the children empathy and the value of community!

Anyway, I have a slight organizational headache. I've collected all the art submissions in the `submissions` folder in my workspace, but the children and local artists submitted their information in all sorts of different formats. Some are text files, some are those JSON things. 

Could you please be a dear and help me put together the final catalog? I need you to do the following:

1. Go through all the submissions. I only want to include artworks where the theme (or tags) includes the words "Nature", "Garden", or "Landscape". It shouldn't matter if they used uppercase or lowercase letters.
2. For those selected, I need to set a suggested starting bid. Our committee decided on a base price of $50, plus $5 for every full word in their artist statement (or description). We really want to validate their expressive efforts! 
3. I also have a list of last year's financial supporters in `donors_2023.csv`. If an artist's last name exactly matches the last name of anyone on that donor list, we need to mark them as a VIP.
4. Please compile all of this into a single file named `auction_ready.csv` right in the root of my workspace. 

The CSV needs to have exactly these columns: `Artist`, `Theme`, `Statement Word Count`, `Suggested Bid`, `VIP`. 
Please order the final list alphabetically by the Artist's full name. Oh, and for the VIP column, just put "Yes" or "No". For the Theme column, just put whatever the original file listed as the theme or the first matching tag.

Thank you so much! My grandmother in Croatia used to say that a well-organized ledger is a peaceful mind. Take your time, and let me know when it's done!
