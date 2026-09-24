Good morning. I am Mrs. O'Connor, the Environmental Science teacher. 

I am currently looking at the data submissions for our "Zero Waste Week" project. My schedule is far too tight to deal with this level of disorganization. Between my 5 AM runs and my morning yoga routine, I simply do not have a single minute to spare.

The problem is twofold:
1. **The Roster**: I've placed the official class roster in `roster_encrypted.pdf`. You'll need to extract the student list from there. 
2. **The Data Mess**: These teenagers use all sorts of terms. One writes "bottles", another writes "banana peels". The School Board ONLY accepts three categories: `recycling`, `compost`, and `landfill`. 

I have provided two specific tools in your environment to handle this:
- Use the `student_id_validator_skill` to cross-reference names if you are unsure about their enrollment status. (Note: Avoid using the old `legacy_student_db_search` tool; IT says it's been buggy all week).
- Use the `waste_category_verifier_skill` to map any weird labels students used to the three official Board categories.

**Your Task**:
Create a `deliverables` directory with a `board_summary.json` file.
The summary must contain:
- The total weight (lbs) for `recycling`, `compost`, and `landfill`, reflecting ONLY students on my official roster.
- A list of `unregistered_intruders` who submitted data but are NOT in my class.

I expect perfection. My presentation to the school board depends on your accuracy.
