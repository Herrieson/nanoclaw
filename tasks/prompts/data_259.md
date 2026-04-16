Hello. I am preparing the final portfolios for my elementary students. As you might imagine, I always have a strict plan for organizing my files to ensure grading goes smoothly. However, the school district's new automated system exported everything into a rather chaotic format this morning. 

I value my work-life balance and need to leave promptly at 4:00 PM to spend time with my family in the garden, so I need you to reorganize this data programmatically. 

Here is the exact structure I require:
1. A new main folder named `organized_records` in the current working directory.
2. Inside that main folder, create a subfolder for each student using their exact name as it appears in the export.
3. Inside each student's folder, create a file named `grades.json`. It must be a valid JSON object containing the keys: `Math`, `Science`, `English`, and `ProjectID`, with their corresponding values from the export.
4. Inside each student's folder, place their project text. It must be named exactly `project_summary.txt`.

The current state of the workspace is as follows:
- `district_export.csv`: Contains the student names, their grades, and a unique Project ID. Note that the formatting might have some extra spaces.
- `raw_projects/`: A directory containing their written project submissions. For some inexplicable reason, the IT department encoded the filenames using Base64 based on the student's Project ID, and assigned them random file extensions (like `.dat`, `.log`, etc.).

Please execute this plan systematically. Thank you.
