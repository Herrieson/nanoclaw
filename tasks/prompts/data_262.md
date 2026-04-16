Listen carefully. I do not have time for incompetence. The previous administrative staff left our scheduling system in absolute shambles, and with the upcoming district audit, I am spending my personal time planning and fixing this mess instead of preparing my staff. 

I've dumped the raw files into the `./` directory. Here is exactly what is wrong and what I need you to do:

1. Look at `staff_schedule.txt`. The dates are completely inconsistent—some are MM-DD-YYYY, some are YYYY/MM/DD. Worse, someone was apparently taking notes during meetings and their voice-to-text or whatever picked up my meeting habits. There are annoying little notes like `[doodle: star]` or `~drawing lines~` scattered throughout the text. These must be completely ignored.
2. Look at `absences.log`. It lists times when staff members were absent and need to be deducted from their scheduled shifts. 
3. I need you to calculate the *exact* number of hours each staff member is actually working per day, after subtracting any absent hours.
4. Output the pristine, perfectly organized result as a JSON file named `final_schedule.json` directly inside the `./` directory.

The JSON structure must be exactly like this:
