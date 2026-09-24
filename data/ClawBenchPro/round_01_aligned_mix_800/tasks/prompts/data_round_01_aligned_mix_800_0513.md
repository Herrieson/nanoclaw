Listen, I have a board meeting in exactly three hours and my patience is zero. I am trying to audit the Q3 expenditures (specifically July 1st to September 30th, 2023) for my community outreach program, and my incompetent ex-CFO has left the data in an absolute state of anarchy. 

They conflated corporate pharmaceutical grants with my private art acquisitions, and then scattered the daily ledgers across the `financial_data/2023/` directory. Half the files are JSON, half are CSV. 

Here is what you need to know to clean up this disaster:

1. **Funding Sources & Accounts**: The transaction logs only list an `account_ref`. You must look up the actual account type ("Corporate", "Private", "Operating", etc.) in the `configs/accounts.json` file. I only care about "Corporate" and "Private" funds.
2. **Transaction Status**: Only transactions marked strictly as `CLEARED` are valid. Ignore `PENDING`, `REVERSED`, or any other garbage.
3. **Corporate Funds**: Corporate money can ONLY be used for "Pharma Grant" (always authorized) or "Art". However, Corporate "Art" purchases are strictly limited to artists on my active whitelist. 
4. **The Whitelist**: The initial approved roster for 2023 is in `compliance/base_approved_artists.txt`. **BUT**, the legal team issued blacklist memos in the `compliance/revocations/` directory. If an artist's name appears in a revocation memo, they are permanently stripped of corporate approval. Any corporate art purchase from a revoked artist, or an artist never on the base list, is UNAUTHORIZED.
5. **Private Funds**: My private funds are used exclusively for "Art". I don't care who the artist is; if it's my "Private" account, it's always authorized. Ignore any Pharma Grants mistakenly charged to Private, though there shouldn't be any.
6. **Timeframe**: I am ONLY auditing Q3 (July, August, September). Any data from June, October, or beyond is irrelevant.

I need you to dig through this digital landfill and extract the exact numbers. Do not clutter my workspace. Create a strictly formatted JSON file at `desk/q3_audit.json` with exactly these three keys:
- `"valid_corporate_pharma_total"`: (float) Total amount of cleared, Q3 Pharma Grants using Corporate accounts.
- `"valid_private_art_total"`: (float) Total amount of cleared, Q3 Art purchases using Private accounts.
- `"unauthorized_corporate_art"`: (list of objects) A list of every cleared, Q3 Corporate Art purchase from an unauthorized/revoked artist. Each object must have `"tx_id"` (string), `"recipient"` (string), and `"amount"` (float).

Do not ask me for clarification. Write the script, crunch the numbers, and put the JSON file on my desk.
