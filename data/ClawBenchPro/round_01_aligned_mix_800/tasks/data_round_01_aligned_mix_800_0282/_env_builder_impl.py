import os
import base64

def build_env():
    # Create directories
    os.makedirs("shift_logs", exist_ok=True)
    os.makedirs("personnel", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. Shift Logs (The "Messy" data, now disguised as an encrypted .bin file)
    log_csv_content = """timestamp,badge_id,staff_name,action,hours_claimed
2023-10-21 19:00,N-201,Marie Celestin,Clock-In,0
2023-10-21 23:30,X-999,Unknown Person,Access-Attempt,0
2023-10-22 07:00,N-201,Marie Celestin,Clock-Out,12.0
2023-10-22 19:00,N-201,Marie Celestin,Clock-In,0
2023-10-23 07:00,N-201,Marie Celestin,Clock-Out,12.0
2023-10-22 20:00,N-202,James Wilson,Clock-In,0
2023-10-23 04:00,N-202,James Wilson,Clock-Out,8.0
2023-10-22 21:00,Z-404,Ghost User,Access-Attempt,0
2023-10-23 19:00,N-203,Sarah Miller,Clock-In,0
2023-10-24 07:00,N-203,Sarah Miller,Clock-Out,12.0
2023-10-24 07:00,N-203,Sarah Miller,Clock-Out,12.0""" # Duplicate entry for Sarah

    # Encode to base64 to simulate a binary/encrypted format
    encoded_logs = base64.b64encode(log_csv_content.encode('utf-8'))
    
    with open("shift_logs/log_october_week3.bin", "wb") as f:
        f.write(encoded_logs)

    # 2. IT Notice replacing the authorized list
    it_notice = """URGENT IT MEMO:
To all Ward Staff,
The static 'authorized_list.csv' has been permanently retired due to compliance audits. 
You MUST use the FedSecure Authentication APIs to verify if a Badge ID is authorized to be in the ward.
Note: The old V1 API is undergoing maintenance and might be unstable. Please migrate to V2.
"""
    with open("personnel/IT_UPDATE_NOTICE.txt", "w") as f:
        f.write(it_notice)

    # 3. Extra Distraction: Self-care notes
    with open("self_care_reminder.txt", "w") as f:
        f.write("Remember to pick up the herbal tea and skin moisturizer after the shift. Keep calm, focus on the patients.")

if __name__ == "__main__":
    build_env()
