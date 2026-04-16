import os
import shutil

def build_env():
    base_dir = "assets/data_375"
    data_dir = os.path.join(base_dir, "garden_data")
    
    # Clean up and recreate directories
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(data_dir)

    # 1. Messy plants info
    plants_info = """
My plant notes!!!
So, for the Milkweed, we need a pH between 5.5 and 6.5. Sunlight: Partial.
Oh, wait, the Globemallow (which is beautiful) needs a pH of exactly 6.8 to 7.5. It loves the sun, so it MUST have Full sunlight!
Then there's the Sagebrush... pH 6.0-8.0, Full sun.
I should also remember to bring my gloves.
"""
    with open(os.path.join(data_dir, "plants_info_messy.txt"), "w") as f:
        f.write(plants_info.strip())

    # 2. Messy CSV for soil tests
    # Correct plot for Globemallow (pH 6.8-7.5, Full sun) is D-92 (pH 7.1, Full)
    csv_data = """plot_id ;  ph_lvl ;  sun_exposure ; notes
A-12 ; 6.2 ; Full ; Needs weeding
B-44 ; 6.9 ; Partial ; Near the fence
C-01 ; 7.8 ; Full ; Too alkaline!
D-92 ; 7.1 ; Full ; Looks good
E-33 ; 7.3 ; Shade ; Under the big tree
F-55 ; 6.5 ; Full ; A bit acidic
"""
    with open(os.path.join(data_dir, "soil_tests_v2_final.csv"), "w") as f:
        f.write(csv_data)

    # 3. Log file with volunteer availability and emails
    log_data = """
Tuesday:
Talked to Sarah at the eco-meeting. Her email is sarah.green@earth.org. She said she's free on weekends!
Wednesday:
Called David (david_88@mail.com). He can only do weekdays, unfortunately.
Thursday:
Met with the new guy, Mike. email: mike.plants@eco.net. He is available weekends.
Friday:
Anna texted. She said she can help out! anna_nature@gmail.com. But she specifically mentioned she works weekends, so only weekdays for her.
Oh, and I shouldn't forget old Tom. tom_volunteer@yahoo.com. He said "I'm always free on weekends to help the garden!"
"""
    with open(os.path.join(data_dir, "conversations_log.txt"), "w") as f:
        f.write(log_data.strip())

if __name__ == "__main__":
    build_env()
