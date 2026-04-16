'Hell is empty and all the devils are here.' I simply cannot fathom the sheer level of incompetence I am surrounded by every single day. I'm adjusting my glasses right now just trying to process this mess. 

The district office sent over the reading assessment data in some absurd format. I need this processed immediately so I can assign the students to their literature intervention tiers. The student roster is at `school_data/roster.csv` and the raw scores are logged in `school_data/assessment_raw.txt`. 

Generate a proper `school_data/intervention_list.csv` with exactly these columns: `student_id`, `full_name` (First and Last name combined with a space), `latest_score`, and `tier`. 
For the tiers: below 60 is "Intensive", 60 to 79 is "Strategic", and 80 or above is "Benchmark". If a student is missing from the score logs, their score is 0 and they are "Intensive". Note that some students took the assessment multiple times; only use their *latest* chronological score.

Furthermore, some imbecile managed to sabotage my personal book review blog. In `blog/reviews/`, someone replaced every mention of the great Bard with `<span class="redacted">CENSORED</span>` and injected vile `<script>` tags throughout my markdown files. Restore Shakespeare's name and completely remove all `<script>...</script>` blocks (and their contents). 

'If you can look into the seeds of time, And say which grain will grow and which will not, Speak then to me.' I expect this done flawlessly and without delay.
