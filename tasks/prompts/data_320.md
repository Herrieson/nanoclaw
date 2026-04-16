As Alexander Pope wisely noted, "A little learning is a dangerous thing; drink deep, or taste not the Pierian spring." Looking at the district's recent reading metrics, I am convinced our students are entirely parched. But my immediate crisis is not just their lack of taste—it is the sheer incompetence of our district IT vendor.

They migrated the student reading logs into a frankly offensive, malformed file named `reading_logs_corrupted.csv`. I am an Education Administrator overseeing multiple schools; I am *not* a data janitor. The superintendent expects my curriculum allocation report by tomorrow morning, and my blood pressure is already dangerously high just looking at this mess.

In the same directory, you will find my personal literary review database, `blog_books.db`. It contains a table of books I have meticulously reviewed and categorized. Some are timeless classics (`is_classic = 1`), and others are modern drivel.

Here is what you must do, and I will not repeat myself:
1. Parse that atrocious CSV file. The titles are rife with erratic capitalization and trailing spaces. Fix them.
2. Cross-reference the reading logs with my SQLite database.
3. I only care about the students reading actual literature. Discard any entries for books not marked as classics in my database.
4. Calculate the total reading time each student spent on these Approved Classics. The logs are in minutes, but I require the final report to be strictly in **HOURS**, rounded to exactly two decimal places.
5. Output the final data as a simple JSON dictionary mapping the student's name to their total hours. Save it to `reports/classic_readers.json`. Create the directory if it doesn't exist.

Do it correctly the first time. I do not have the patience for trial and error today.
