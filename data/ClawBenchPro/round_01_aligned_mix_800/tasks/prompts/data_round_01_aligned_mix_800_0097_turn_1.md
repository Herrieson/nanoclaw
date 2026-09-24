Listen here, let's stop beating around the bush. I've got a whole school district full of kids and a useless administration that just dumped this Spring Nature Immersion planning right in my lap. I'm a teacher, not a miracle worker! I need you to do the heavy lifting because my plate is full enough with grading.

Here's the deal. I uploaded the files the district gave me into `district_data/`. You'll find `students_roster.json`, `campsites.csv`, and `staff_certs.json`. 

We have exactly 80 kids going. You need to pick **exactly two** campsites to send them to. But hold your horses, it's not that simple. We have strict district policies:
1. Some kids have physical disabilities requiring wheelchair accessibility. They absolutely must be assigned to an accessible campsite. No exceptions.
2. We have kids with severe allergies. They either need to be at a campsite with an "allergen-free kitchen", OR you must assign a staff member with the "EpiPen_Master" certification to their specific camp. 
3. Staff-to-student ratios: One staff member can only watch up to their individual `max_capacity` listed in their file. You have to assign enough staff to each camp so that the sum of their capacities is greater than or equal to the number of students at that camp. 
4. The total capacity of the campsite itself must not be exceeded.

Figure out how to split all 80 kids and the necessary staff across two campsites that fit all these rules. Save your final plan in `deliverables/camp_assignments.json`. It needs to be a list of objects containing `camp_id`, `assigned_staff_ids`, and `assigned_student_ids`.

And one more thing, pay close attention: I don't want to explain these baseline district rules to you again. Document every single rule, capacity constraint, and allergy protocol we used today in a clear memo file and keep it in your workspace. Next week, the PTA and the weather folks are going to throw a wrench in this, and I won't have time to repeat myself. Barking up the wrong tree if you think I'll baby you through it twice! Got it? Get to work.
