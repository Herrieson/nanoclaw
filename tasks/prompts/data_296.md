Hello there. I am currently finalizing the reading assessments for my middle school students. While I usually pride myself on having a strict plan and keeping things highly organized, my students submitted their reading logs in a few different formats this week, and it has become a bit of a data puzzle.

I need to upload their total pages read to the district's new grading portal, but my time is better spent preparing tomorrow's lesson plans and spending the evening with my family. 

Here is what I have prepared for you in the `./` directory:
1. A folder named `raw_logs` containing the students' submissions as text files.
2. Our class roster in a SQLite database named `students.db`, which contains the official student IDs.

Could you please process these logs, match each student's name to their corresponding ID in the database, calculate the total pages read for each student, and generate a final JSON file named `upload_payload.json` in the `./` directory? 

The final JSON file must be a list of objects, each containing exactly two keys: `student_id` (an integer) and `total_pages` (an integer). 

Thank you very much for your assistance. Clear and accurate data is essential for their assessments.
