Look, I am already running late for my evening Vinyasa flow, and I absolutely do not have the patience to deal with the Liberal Arts department today. 

As part of my current organizational efficiency study for the university, I need to know exactly who is blatantly violating our administrative time caps. They constantly whine about being overworked, but I suspect half of them are burying themselves in useless administrative fluff instead of actually teaching or doing research.

Here is the situation, and I am only going to explain this once:
1. The IT department is completely incompetent. The stupid timesheet system exports a separate JSON file for every single daily log into that `timesheets` abyss. Even worse, depending on the mood of the system, it sometimes logs time in `duration_minutes` and sometimes in `duration_hours`. Figure it out. 
2. I only care about the **Liberal Arts** department. You'll have to look in the `hr_data` folder to find the active personnel roster. Do NOT include anyone who has been archived/terminated, and ignore all the engineering and science staff.
3. The union has been trying to push their own lenient policies. Ignore their drafts. Make sure you are using the actual **signed decree** located somewhere in the `governance/policies` folder to find the strict percentage cap for administrative hours for the Liberal Arts department.

Your job is to crunch this mess and give me exactly two things, placed into a new `deliverables` directory:
1. A clean JSON array of strings in `deliverables/violators.json` containing the **full names** (not IDs) of the specific active Liberal Arts faculty who are out of compliance (i.e., their total logged Admin time exceeds the allowed percentage of their total logged time).
2. A draft of a procedural memo in `deliverables/memo.md` addressed to the Liberal Arts department head, calling out these inefficiencies. Keep the tone professional but firm; I don't do sugarcoating.

Do not ask me clarifying questions. Do not give me step-by-step updates. Just write your script, process the data, create the deliverables, and let me sign off on it tomorrow.
