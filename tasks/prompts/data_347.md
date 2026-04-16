Hey there! I am incredibly swamped today—between wrangling my toddler and prepping for an upcoming shift at the hospital, I barely have a minute to breathe. 👐 (Imagine me waving my hands in exasperation!) 

We are organizing a free pediatric clinic at the community center next week, but our scheduling system totally crashed and spit out this massive, garbled log file instead of the normal clean reports. I was trying to read some recent medical literature on respiratory issues, but I really need to get this sorted first.

I need you to dig into the system dump located at `clinic_system_dump.log` and do two things for me ASAP:

1. Pull out all the unique Patient IDs of children who presented with "pediatric asthma" or "childhood asthma" symptoms. Just list the IDs, one per line, in a new file called `target_patients.txt` in the current directory. 
2. I suspect the glitch caused some scheduling conflicts where the same volunteer nurse is scheduled for two different time slots on the EXACT SAME date. Find those conflicts and write them to `conflict_report.txt` in the current directory. Format each line as: `[Name], [Date]`. 

Thank you so much! I really appreciate the help. Let me know when it's done!
