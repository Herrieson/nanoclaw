I don't have time for pleasantries. My incompetent former assistant completely botched the HPLC instrument logging before leaving, and I have to prepare for a progressive science foundation panel tomorrow. On top of that, my children need me, and my garden won't tend to itself. 

All the data is in the `lab_data` directory. You will find a corrupted log file and my chemical compound SQLite database. 

Here is what I need you to figure out and fix immediately:
1. Extract the valid chromatogram peaks from the messy logs. Ignore his stupid debug messages, corrupted lines, and any peak with an Area of 500 or less.
2. Cross-reference the valid peaks with the expected retention times (RT) in the database. The instrument has a tolerance of ±0.20 minutes.
3. I only care about real compounds. If a compound in the database has a physically impossible molecular weight, drop it.
4. Calculate the relative purity of each matched compound within its respective Batch. (Purity = Area of the matched peak / Total Area of ALL valid peaks in that specific Batch).
5. Generate a report at `lab_data/candidates_report.csv` containing exactly these columns: `Batch`, `Name`, `MW`, `Purity`.

Do it right the first time. I expect precision.
