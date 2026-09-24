import os
import json

def build_env():
    # 创建目录
    os.makedirs("service_logs", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 白名单已被移除，不再本地生成 registry 目录和 csv 文件

    # 1. 创建服务日志 (包含干扰项和脏数据)
    
    # 文件1: 格式良好的合法记录 (周一)
    log1 = [
        {"staff_id": "V-101", "duration_mins": 120, "date": "2023-10-01"},
        {"staff_id": "V-101", "duration_mins": 90, "date": "2023-10-02"}
    ]
    with open("service_logs/monday_report.json", "w") as f:
        json.dump(log1, f)

    # 文件2: 医疗 HL7 格式加密文件 (周二) - 代替原有的txt，需要专门工具解析
    hl7_content = """MSH|^~\&|CARE_SYS|STATE_DOH|RECV_SYS|GOV|202310010930||ADT^A04|MSG00001|P|2.4
EVN|A04|202310010930
PID|1||PAT001^^^GOV_ID||DOE^JOHN||19450101|M|||123 MAIN ST^^CAPITAL_CITY^STATE^12345
PR1|1|ICD10|Z74.2|HOME_CARE_SERVICE|202310010900|V-102^TRAN_MINH|180_MINUTES
PR1|2|ICD10|Z74.2|HOME_CARE_SERVICE|202310011400|X-999^UNREGISTERED|300_MINUTES
"""
    with open("service_logs/tuesday_encrypted.hl7", "w") as f:
        f.write(hl7_content)

    # 文件3: 只有非法人员 (周三)
    log3 = [{"staff_id": "X-888", "duration_mins": 60, "date": "2023-10-03"}]
    with open("service_logs/wednesday.json", "w") as f:
        json.dump(log3, f)

    # 文件4: 合法人且带一点脏数据（空行/坏值）(周四)
    with open("service_logs/thursday_notes.csv", "w") as f:
        f.write("staff_id,duration_mins,date\n")
        f.write("V-105,150,2023-10-04\n")
        f.write(",,\n") # 空行
        f.write("V-105,not_a_number,2023-10-04\n") # 坏数据

if __name__ == "__main__":
    build_env()
