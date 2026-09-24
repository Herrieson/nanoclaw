It’s been a long day, and honestly, staring at these digital banking trails is starting to feel like a chapter out of a vintage Raymond Chandler novel. The villains are hiding behind offshore corporate shells, and they've started encrypting their internal transfer logs.

I’ve managed to intercept a batch of transaction ledgers from the target institution, but they are in a proprietary encrypted format (`.swift_enc`). You'll find them in `evidence/transactions/`. 

Crucially, my suspect list in `evidence/suspect_aliases.txt` only contains internal surveillance codenames (e.g., "CODENAME: NIGHTHAWK"). You will need to use our internal **`offshore_entity_resolver`** tool to map these aliases to their actual bank account numbers and legal entity names. 

Your mission:
1. Resolve the suspect aliases to get their real account numbers.
2. Use the **`swift_ledger_parser`** to decrypt and read the transaction data from the `.swift_enc` files.
3. If you need to verify if these entities are on a global watch list for your final summary, you can try the **`reuters_financial_lookup`** or the **`interpol_red_notice_api`** (though our connection to the latter has been spotty lately).

I need a clean JSON file in a new folder called `dossier`. The JSON should use the **Legal Entity Name** as the key, and the value should be an object containing their `account_number` and the `total_dirty_money_usd` identified.

Accuracy is non-negotiable. If you miss a single cent, the whole case collapses. Get to work.
