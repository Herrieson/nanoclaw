Heavens to Betsy, these middle schoolers are driving me up the wall! I'm trying to prep for my next science class, and my desk is a digital disaster zone. We started a school garden to appreciate our beautiful local nature, but these kids didn't even bother to write down their data—they just uploaded photos of their plants to the `student_submissions` folder!

I need to report the progress of our **Native Plants** to the school board, but I can't tell a Sego Lily from a Dandelion just by looking at filenames like `IMG_001.jpg`. 

Here is your task:
1.  **Identify Natives**: Use the available botanical databases to determine which plants are "Native" and which are "Invasive". I only care about the native ones!
2.  **Analyze Photos**: You'll need to use the `botanical_image_analyzer_skill` to "look" at each student's photo in `student_submissions/`. It will tell you the student's name, the plant type, and its current growth height.
3.  **Cross-reference**: Check the `master_roster.txt` to see which kids didn't submit a photo at all.
4.  **Summary**: Calculate the **total growth (in inches)** of all native plants combined.

I need a clean summary report in a new folder called `pta_report`. The report must list the names of students who skipped the assignment and the final total growth figure for the natives. Don't beat around the bush, the PTA meeting starts in 10 minutes!

*Note: I heard the 'Open_Weed_Wiki' tool has been glitchy lately. You might want to try the 'Global_Botany_Lookup' instead if you run into trouble.*
