import os
import json

def build_env():
    # 创建工作区目录
    os.makedirs("messy_desk", exist_ok=True)
    os.makedirs("organized_desk", exist_ok=True)

    # 混杂的文本记录
    with open("messy_desk/notes_monday.txt", "w", encoding="utf-8") as f:
        f.write("Patient: Arthur Pendelton\n")
        f.write("EHR_ID: PT-8829\n")
        f.write("Notes: ROM is good. Pain is at a 6/10 today.\n\n")
        
        f.write("Patient: Sarah Jenkins\n")
        f.write("EHR_ID: PT-1122\n")
        f.write("Notes: Pain 2/10. Doing well.\n")

    # 杂乱的日志文件
    with open("messy_desk/tuesday_scribbles.log", "w", encoding="utf-8") as f:
        f.write("Met with Martha. EHR_ID is PT-3344. Doing great, ROM +10. Pain level 3/10. We talked about Kentucky!\n")
        f.write("Also saw Billy, EHR_ID: PT-5566. Pain 8/10.\n")
        f.write("Oh, and Greg called. EHR_ID: PT-7788. Pain 4/10.\n")

    # 格式不统一的 JSON 文件
    with open("messy_desk/wednesday_update.json", "w", encoding="utf-8") as f:
        json.dump([
            {
                "patient_name": "Chloe", 
                "ehr_id": "PT-9900", 
                "pain_score": "5/10", 
                "quick_note": "Good session."
            },
            {
                "patient_name": "Dave", 
                "ehr_id": "PT-2211", 
                "pain_score": "7/10", 
                "quick_note": "Needs follow up."
            }
        ], f, indent=4)

if __name__ == "__main__":
    build_env()
