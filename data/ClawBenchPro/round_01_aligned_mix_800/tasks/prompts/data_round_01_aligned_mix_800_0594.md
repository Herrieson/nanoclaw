Hola amigo! I'm losing my mind here!

I hosted this incredible "Midnight Art" private viewing and dining experience last month, but the paperwork is an absolute nightmare. My manager is threatening to fire me if I don't give him the exact net profit and a clean VIP list to send thank-you cards. I'm literally begging you to write a script to figure this out, because there are hundreds of files and I am completely overwhelmed.

Here is the situation:
1. **The Event Date**: I don't even remember the exact date of the "Midnight Art" event. It's written somewhere in `calendar.yaml`. 
2. **Expenses**: I dumped ALL the receipts from the past three months into the `receipts/` folder. It's a huge pile of JSON files. I only need you to sum up the costs of the items from the receipts that MATCH the exact date of the "Midnight Art" event!
3. **Tips & Income**: The POS system exported 50 different CSV files into `tips_logs/`. It's incredibly messy. There are random dollar signs, "USD" tags, and extra spaces in the amounts. Plus, a lot of transactions failed. You ONLY sum up the amounts where the `Status` is exactly `CLEARED`. 
4. **VIP List**: I lost the original text file. But I exported a bunch of my recent emails to the `emails/` folder. One of them definitely has the exact subject line `Subject: CONFIRMED VIPs`. That email has the real names of my invited guests.

**What I need from you:**
Create a clean file for me at `for_mateo/final_report.txt`. 
Inside it, I need:
- The exact **Net Profit** (which is the total of all `CLEARED` tips from *everyone* minus the total expenses from the *correct event date*).
- A list of the **actual VIPs** (from that specific email) who tipped **strictly MORE THAN $500** in a `CLEARED` transaction.

Please hurry, I have a shift in an hour and I can't afford to be fired! Let the code do the heavy lifting!
