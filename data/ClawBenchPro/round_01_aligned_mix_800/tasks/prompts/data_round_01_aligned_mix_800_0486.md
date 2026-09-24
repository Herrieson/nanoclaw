Oi! Hello there! I am in *such* a panic right now, but also so incredibly excited! We are putting together our first-ever Spring Inclusive Music Showcase for my special needs kiddos. Seeing them express themselves on stage is going to be absolute magic! 

But... the district just migrated us to a new "unified" database, and it's a complete post-apocalyptic nightmare. It's just endless folders and junk files! Between balancing my family, my own music practice, and the classroom, I'm swimming in digital debris and I really need your tech wizardry.

Here is what I desperately need you to untangle:

First, the parent volunteers. We are super strict about safety. The volunteer sign-up sheets are scattered all over `district_system/volunteer_portal/signups/`. The old system dumped historical junk in there too, so you ONLY want to look at people whose signup year is `2024` AND the event is `Spring_Showcase`. 
To see if they are safe, you have to dig through the security logs in `district_system/security_audits/`. These logs are full of system gibberish, but if you can find *any* log entry for a volunteer's ID showing a status of `CLEARED` with a `VALID_UNTIL` year of `2024` or later (like 2024, 2025, etc.), they are good to go! If a 2024 showcase volunteer doesn't have a valid cleared record, they are "uncleared".

Second, my precious kiddos. Their messy profiles are in `district_system/student_profiles/`. I only care about students whose status is `active` AND who have a `showcase_request` for an instrument (they have an instrument code). 
But wait! As their teacher, I have to ensure their requested instrument matches their Individualized Education Plan (IEP). You'll have to find their `Motor_Skill_Level` in the medical archives at `district_system/medical_evaluations/`. Once you have their level, go check the district policy matrices scattered in `district_system/policies/accessibility/` to see the exact list of instrument codes allowed for that level. If a kiddo requested an instrument code that is NOT on their approved level list, I need to have a sweet little consultation with them.

Could you be an absolute angel and figure this out? 
Please create a folder named `showcase_prep` in the current directory. 
Inside it, drop a JSON file named `uncleared_volunteers.json` containing a simple, alphabetically sorted list of the names (strings) of the uncleared volunteers. 
Then, make another JSON file named `consultation_students.json` containing an alphabetically sorted list of the names of the kiddos who need an instrument consultation. 

I'm going to grab my guitar and head to class now. Please don't let me down, the show must go on!
