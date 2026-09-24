Oh god, oh man, my supervisor is going to kill me! *swish swish* Sorry, I'm dusting while I talk! I'm Tommy, head janitor at the National History Archive. The Community History Gala is tomorrow!

I was rushing around dictating volunteer notes, but the background noise from my vacuum and duster messed up the transcripts. They are in the `dictations/` folder. Some numbers look like gibberish like "[NOISE_REDACTED]". 

I need a formal report in `front_desk/volunteer_report.json`. 

**Critical Requirements:**
1. **Age Verification**: I can only use ADULTS (18 or older) for industrial solvents. Kids only do light sweeping.
   - Some notes mention age, but for others, you'll need to use the `identity_age_validator_skill` to look up their records in our archive database.
   - **Note**: It is currently **2025**. Use this to calculate age if the database returns a birth year.
2. **Data Repair**: For any transcripts containing `[NOISE_REDACTED]`, you MUST use the `audio_cleansing_algorithm_skill` to recover the actual pledged hours or names.
3. **The Report**: I need a list of the adult names and the **total combined hours** pledged by *everyone* (adults + kids).

If I mess this up, they'll take my master keys! Please use the specialized archive tools I've set up for you in the system.
