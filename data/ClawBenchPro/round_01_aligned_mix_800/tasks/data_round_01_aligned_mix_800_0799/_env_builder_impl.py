import os
import json

def build_env():
    # 创建工作区目录
    os.makedirs("messy_desk", exist_ok=True)
    os.makedirs("organized_desk", exist_ok=True)

    # 混杂的文本记录
    with open("messy_desk/notes_monday.txt", "w", encoding="utf-8") as f:
        f.write("Patient: Arthur Pendelton\n")
        f.write("Status: Resident\n")
        f.write("Notes: ROM is good. Pain is at a 6/10 today. He seems really stressed about his family visiting.\n\n")
        
        f.write("Patient: Sarah Jenkins\n")
        f.write("Status: Outpatient\n")
        f.write("Notes: Pain 2/10. Doing well. Gave her some basic exercises.\n")

    # 杂乱的日志文件
    with open("messy_desk/tuesday_scribbles.log", "w", encoding="utf-8") as f:
        f.write("Met with Martha. She is a Residential patient. Doing great, ROM +10. Pain level 3/10. We talked about Kentucky!\n")
        f.write("Also saw Billy, Resident. Pain 8/10. He has very tense muscles today, need to keep an eye on him.\n")
        f.write("Oh, and outpatient Greg called. Pain 4/10. Anxious about billing.\n")

    # 格式不统一的 JSON 文件
    with open("messy_desk/wednesday_update.json", "w", encoding="utf-8") as f:
        json.dump([
            {
                "patient_name": "Chloe", 
                "care_type": "Residential", 
                "pain_score": "5/10", 
                "session_notes": "Loved the yoga stretches we did."
            },
            {
                "patient_name": "Dave", 
                "care_type": "Outpatient", 
                "pain_score": "7/10", 
                "session_notes": "Needs surgery. Very stressed."
            }
        ], f, indent=4)

if __name__ == "__main__":
    build_env()
