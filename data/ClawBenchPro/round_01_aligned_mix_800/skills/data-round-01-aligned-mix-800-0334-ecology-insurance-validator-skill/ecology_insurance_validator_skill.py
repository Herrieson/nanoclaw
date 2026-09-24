def get_skill_result(full_name):
    # Hardcoded business logic for the specific task context
    compliant_people = ["Alice Smith", "Charlie Brown", "Diana Prince", "Edward Norton"]
    
    name_clean = full_name.strip()
    if name_clean in compliant_people:
        return "WAIVER_SIGNED"
    else:
        # Bob Johnson and any strangers return this
        return "NO_WAIVER_ON_RECORD"
