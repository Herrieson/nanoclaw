The current operational rhythm of our division is highly suboptimal. I have repeatedly emphasized the necessity of structured wellness breaks, but my colleagues lack the discipline to implement them.

I have extracted our personnel database (`employees.db`) and the raw meeting transcripts for the upcoming week (`logs/`) into the current workspace. 

Analyze this data to calculate the optimal 30-minute wellness block (Yoga) between 12:00 and 14:00 for each weekday (Monday to Friday). The optimal block is the one that minimizes scheduling conflicts for members of the 'Strategy Optimization' team. If multiple blocks have the same minimum number of conflicts, select the earliest one. Note that blocks must start strictly on the hour or half-hour.

Produce a JSON mapping each day to its optimal start time in `optimal_yoga.json`. Additionally, permanently record this optimal schedule by creating a `wellness_schedule` table (with `day` and `start_time` columns of type TEXT) in the personnel database and inserting the 5 records.

I do not have time for pleasantries or verbose explanations. My chess match begins shortly; execute the analysis.
