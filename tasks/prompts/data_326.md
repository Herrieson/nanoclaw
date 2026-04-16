The automated ETL pipeline for our trade logs failed overnight due to upstream format changes. I require a clean, standardized database for my end-of-day analysis. 

The raw trade logs are located in `/workspace/raw_data`. They are highly inconsistent: varying date formats, missing headers, and inconsistent delimiters.

Your tasks are as follows:
1. Initialize an SQLite database at `/workspace/trades.db`.
2. Create a table named `transactions` with the following schema: `date TEXT, ticker TEXT, side TEXT, quantity REAL, price REAL, total_value REAL`.
3. Ingest all CSV files from the `raw_data` directory. 
   - Standardize all dates to the `YYYY-MM-DD` format.
   - Calculate `total_value` as `quantity * price` for each row.
   - Insert the cleaned data into the `transactions` table.
4. Calculate the total trading volume (sum of `quantity`, irrespective of whether it was a BUY or SELL) specifically for the ticker 'BRK.A'.
5. Output this exact numerical value into a plain text file at `/workspace/brka_volume.txt`.

Ensure your logic handles the data anomalies gracefully. I expect precision.
