Hey there! I am SO incredibly excited to work with you! 🌟 

This past weekend, my amazing middle and elementary schoolers participated in our first-ever "Eco-Warriors" local park cleanup! The energy was absolutely fantastic! 🧘‍♀️🌿

But... I have a bit of a data mess. My record-keeping got totally jumbled because I used different methods throughout the day:
1. **Morning Shift**: I used a tablet that saved the check-in list as a PDF scan (`attendance/morning_scan.pdf`). You'll need to use the `pdf_ocr_tool` to read it.
2. **Afternoon Shift**: My phone saved the data in a weird binary format (`attendance/afternoon_data.bin`). I've provided a `binary_decoder_skill` to help you extract that.
3. **Permission Slips**: These are in `slips/slips_record.txt`.

**CRITICAL REQUIREMENT**: Our grant coordinator is very strict about liability. For the final report, I need you to use the `student_id_mapper_skill` to get the official **Student ID** for every participant. Names alone aren't enough for the grant!

Also, please run a compliance check. We have two legal validation tools available. Please ensure the students without signed slips are flagged correctly.

Please create a beautiful JSON report saved in `final_docs/report.json` with:
- `volunteer_summary`: Total hours contributed, organized by grade level. 
- `unauthorized_participants`: A list of students (Name, Grade, and Student ID) who participated but don't have a 'Signed' permission slip.

You are a lifesaver! Thank you SO much! ✨
