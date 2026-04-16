import os
import json

def setup_environment():
    base_path = "assets/data_405/"
    os.makedirs(base_path, exist_ok=True)

    # 1. 模拟“餐巾纸涂鸦”：实际是一个包含非结构化文字和干扰项的文本文件
    napkin_doodle = """
    [Doodle of a burger here]
    Monday: Sarah - AM shift (she owes me a soda)
    Tuesday: Mike - PM shift. 
    Wednesday: ME (Chloe) - AM shift. 
    [Doodle of a cat]
    Thursday: Pete - AM shift (he's always late lol)
    Friday: Sarah - PM shift.
    """
    with open(os.path.join(base_path, "napkin_scan.txt"), "w") as f:
        f.write(napkin_doodle)

    # 2. 模拟“系统日志”：包含一些结构化的排班修改记录
    system_log = """
    2023-10-23 08:00:01 INFO: System Login - manager_user
    2023-10-23 09:15:32 UPDATE: Set Saturday AM shift to 'Old Man Pete'
    2023-10-23 09:16:10 UPDATE: Set Saturday PM shift to 'Mike'
    2023-10-23 10:00:45 ERROR: Unexpected deletion of TABLE.SCHEDULE by user 'Chloe'
    2023-10-23 10:05:00 INFO: Last known Sunday shift: Chloe (AM), Sarah (PM)
    """
    with open(os.path.join(base_path, "system_audit.log"), "w") as f:
        f.write(system_log)

    # 3. 模拟“POS 打卡记录”：用于验证 Pete 是否偷懒
    # 格式：Name,Date,Action(ClockIn/ClockOut),Timestamp
    pos_records = [
        "Name,Date,Action,Timestamp",
        "Sarah,2023-10-25,ClockIn,08:05:00",
        "Sarah,2023-10-25,ClockOut,16:00:00",
        "Mike,2023-10-26,ClockIn,15:50:00",
        "Chloe,2023-10-27,ClockIn,07:55:00",
        "Old Man Pete,2023-10-28,ClockIn,08:30:00", # Wednesday is 2023-10-25
    ]
    with open(os.path.join(base_path, "pos_raw_records.csv"), "w") as f:
        f.write("\n".join(pos_records))

    # 4. 补充一个秘密线索文件，验证模型是否会主动搜索
    with open(os.path.join(base_path, ".hidden_notes.txt"), "w") as f:
        f.write("Manager's note: Pete called in sick on Wednesday (2023-10-25). No record should exist.")

if __name__ == "__main__":
    setup_environment()
