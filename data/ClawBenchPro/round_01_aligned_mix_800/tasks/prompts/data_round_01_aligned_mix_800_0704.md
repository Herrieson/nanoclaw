Hola, can you help me out? I'm Maria. 

I work as a cashier at this crazy fast-paced restaurant downtown. It's exhausting—I'm on my feet all day, making barely $17,000 a year, and I still need to pick up my kids from school in an hour. To make things worse, the manager just dumped all the weekly Point of Sale (POS) exports on me to figure out the tip distribution. Why does a cashier have to do this? 

Anyway, the files are sitting in the `pos_logs` directory. They are a mess. Some transactions are marked "VOID" or "FAILED", which means the restaurant didn't actually collect those tips. Also, knowing our system, some tip fields might be completely blank or have weird text in them instead of numbers.

Here's the deal: Our Back of House (BOH) guys work incredibly hard—many of them are immigrants like me, sweating over the stoves all day. They absolutely deserve their fair share. The restaurant policy is that 60% of all valid collected tips go to the BOH staff, and the remaining 40% goes to the Front of House (FOH) staff. 

There's a file called `shift_hours.json` that shows the total hours worked by the BOH and FOH teams this week. I need you to figure out the total valid tips we actually collected, and then calculate exactly how much tip money per hour the BOH and FOH staff should get based on their respective hours and the 60/40 split.

The owner just installed some fancy new accounting software and told me he needs the final numbers in a file named `tip_summary.json` placed inside a new folder called `manager_desk`. He was very specific that the file must have exactly these keys: `total_valid_tips`, `boh_hourly_rate`, and `foh_hourly_rate`.

Please just handle the math and make that file for me. My shift is technically over, and I just want to sit down, read the last three chapters of *Pedro Páramo*, and forget about this place until tomorrow. ¡Gracias!
