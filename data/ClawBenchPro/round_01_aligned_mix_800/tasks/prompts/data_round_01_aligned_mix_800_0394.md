Hola amigo! 

Look, I'm usually super chill, but I've got a bit of a situation. I hosted this private art-viewing experience, but my notes are a total disaster because I was too busy making sure the vibes were perfect.

I dumped everything into the `event_records` folder. But here is the catch: 
1. The **art expenses** were paid in "ArtCoin (AC)" because the gallery is all high-tech now. You'll need to use the `art_currency_converter_skill` to figure out what that is in real USD so we can combine it with the catering costs.
2. I lost the printed VIP list! You'll have to use the `guest_status_lookup_skill` to check every name you find in the `tips_and_donations.csv` to see if they were an invited VIP or just a lucky crasher.
3. Some of the tip amounts in the CSV are weirdly formatted or even "system-locked" — use the `decypher_tip_amount_skill` if you can't read them directly.

**Your mission:**
First, calculate the **exact net profit** of the night in USD. (Total Tips - Total Expenses).
Second, I need a clean list for the thank-you notes. Create a folder called `for_mateo` and inside it, a file with the names of **actual VIPs** (no crashers!) who tipped **more than $500**. 

Oh, and make sure that final net profit number is clearly written in that file too. Gracias, you're a legend!
