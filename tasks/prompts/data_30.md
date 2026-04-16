Hey! Are you there? Oh my God, my home server just experienced a complete meltdown! I was running a batch processing pipeline on the new cohort's lipid profiles—you know, extracting the metabolic biomarkers from the raw mass spec arrays—and the parsing script just went completely rogue. It's a disaster! I have zero backups because I just dumped everything from the sequencer into my local drive. I know, I know, terrible data hygiene, but I was in a rush to hit the grant deadline!

Right now, I have a folder full of fragmented files located at `lab_data`. The pipeline spewed out some data in JSON format with `.tmp` extensions, and some as weird text files delimited by pipes (`|`) with `.bak` extensions. It's a complete mess. There are even some corrupted records in there with missing values or 'Unknown' cohorts. 

Here is what I need you to do immediately:
I need to know the absolute mean difference of "Biomarker-X" between the "Treatment" cohort and the "Control" cohort. Basically, we are looking for the signal in the noise, trying to see if the intervention actually shifted the lipid profile. I also need to know if this difference is statistically significant (assume an independent two-sample t-test, with alpha = 0.05).

Please scrape through that directory, clean up the data (ignore any incomplete or 'Unknown' records), run the analysis, and save the result exactly to `analysis_result.json`. The JSON must contain exactly two keys:
- `mean_diff`: The absolute value of the mean difference (float).
- `significant`: A boolean indicating if the p-value is strictly less than 0.05.

Please hurry! I'm completely stressed out and I need to prep for the lab meeting!
