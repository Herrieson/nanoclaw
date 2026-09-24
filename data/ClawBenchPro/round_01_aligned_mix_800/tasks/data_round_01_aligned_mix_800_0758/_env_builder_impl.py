import os

def build_env():
    # Create necessary directories
    os.makedirs("site_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Monday log
    with open("site_logs/monday_log.txt", "w") as f:
        f.write("Monday. Crew worked 14 hours total today. It was a long one. \n"
                "Safety issue: Scaffolding on the east wall is missing a guardrail, need to get that fixed ASAP. \n"
                "Also, mental note: I need to buy more cadmium red paint for the garage mural, almost ran out. \n"
                "The kids were surprisingly calm tonight.")

    # Tuesday log
    with open("site_logs/tuesday_log.txt", "w") as f:
        f.write("Tuesday. Kids were crying all morning, gave me a headache. \n"
                "Crew put in 20 hours today to make up for lost time. \n"
                "Hazard spotted: Exposed wiring near the main water line in sector B. Very dangerous. \n"
                "Art hazard: The toddler tried to eat a blue crayon, crisis averted but it was close.")

    # Wednesday log
    with open("site_logs/wednesday_log.txt", "w") as f:
        f.write("Wednesday. Rained out early. Only 8 hours logged for the boys. \n"
                "No major site hazards today, thank God. \n"
                "Need to remember to pick up diapers on the way home. \n"
                "Safety hazard: I left my wooden easel dangerously close to the driveway, almost backed over it with the truck. Gotta be more careful.")

    # Thursday log
    with open("site_logs/thursday_log.txt", "w") as f:
        f.write("Thursday. Good progress on the framing. 22 hours billed. \n"
                "Safety violation: Subcontractors were not wearing hard hats in the overhead drop zone. Yelled at them for that. \n"
                "The sunset was beautiful today, painted a quick watercolor sketch on my lunch break.")

    # Friday log
    with open("site_logs/friday_log.txt", "w") as f:
        f.write("Friday. End of the week, finally. 16 hours. \n"
                "Safety issue: Unsecured trench over 5 feet deep left overnight by the backhoe operator. \n"
                "Gotta write him up. The kids are finally asleep, going to work on my canvas now.")

if __name__ == "__main__":
    build_env()
