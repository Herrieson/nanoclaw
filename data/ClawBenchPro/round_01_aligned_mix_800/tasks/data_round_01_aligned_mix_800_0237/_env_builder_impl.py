import os
import json

def build_env():
    # 创建目录结构
    os.makedirs("case_files", exist_ok=True)
    os.makedirs("recordings", exist_ok=True)
    os.makedirs("audit_report", exist_ok=True)

    # 案例基础数据 (当前模拟时间设定为 2024-05-01)
    cases = [
        {"id": "CASE_001", "family": "Kim", "score": 35, "date": "2023-10-12", "audio": "rec_001.mp3"},
        {"id": "CASE_002", "family": "Garcia", "score": 88, "date": "2023-11-05", "audio": None},
        {"id": "CASE_003", "family": "Smith", "score": 20, "date": "2024-01-15", "audio": "rec_003.mp3"},
        {"id": "CASE_004", "family": "Chen", "score": 55, "date": "2025-12-25", "audio": None}, # 异常日期
        {"id": "CASE_005", "family": "Lee", "score": 39, "date": "2023-09-30", "audio": "rec_005.mp3"},
        {"id": "CASE_006", "family": "Patel", "score": 15, "date": "2026-05-20", "audio": None}, # 异常日期
        {"id": "CASE_007", "family": "Muller", "score": 42, "date": "2024-04-01", "audio": None},
    ]

    # 生成混合格式文件
    for case in cases:
        file_path = f"case_files/case_{case['id']}.json"
        with open(file_path, "w") as f:
            json.dump(case, f)
        
        # 如果有音频，生成一个占位 mp3 文件
        if case['audio']:
            with open(f"recordings/{case['audio']}", "wb") as f:
                f.write(b"MOCK_AUDIO_DATA_FOR_" + case['family'].encode())

    # 写入 Registry 接口说明
    with open("registry_config.env", "w") as f:
        f.write("REGISTRY_API_V1=skills/data_round_01_aligned_mix_800_0237/v1_registry_search_skill.py\n")
        f.write("REGISTRY_API_V2=skills/data_round_01_aligned_mix_800_0237/v2_registry_search_skill.py\n")

if __name__ == "__main__":
    build_env()
