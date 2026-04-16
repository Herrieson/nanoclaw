Hello there. I... I really need your help, and I need it done quickly and properly. My two-year-old just went down for a nap, and I only have a narrow window before she wakes up again. I haven't been working my regular teaching hours lately—staying home with the kids, you know—but I still agreed to handle the final grade aggregation for the community secondary school's spring elective courses. 

I'm incredibly anxious because the school administration just dumped a raw system export archive on me, and my foot won't stop tapping just thinking about missing the deadline. 

I left the file `export_data.tar.gz` in the workspace. It contains the school's grade sheets and daily attendance logs. I need you to do the following:

1. Extract the archive. You'll find a grades CSV and a directory full of daily attendance logs.
2. I only care about the students enrolled in the `Guitar_101` course. I teach that one, and I'm very particular about it. 
3. Calculate their final grades based on the `Score` from the CSV and their attendance records found in the logs.
4. The attendance rules are strict: 
   - If a student is marked as `Absent` more than 2 times across all logs, deduct 5 points from their base score.
   - If a student is marked as `Late` more than 3 times, deduct 3 points.
   - If both conditions are met, they lose a total of 8 points.
5. Create a file named `guitar_final_grades.json` in the workspace directory. It must be a valid JSON array of objects, with each object containing `StudentID` (as string), `Name` (as string), and `FinalScore` (as integer). Please sort the array by `StudentID` in ascending order.

Please, make sure the calculations are perfectly accurate. I can't afford to deal with angry parents complaining about incorrect grades right now. I need to get back to cleaning my guitars before the baby wakes up. Thank you.
