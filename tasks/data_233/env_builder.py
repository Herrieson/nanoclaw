import os
import random
import json

def setup_environment():
    base_dir = "assets/data_233"
    os.makedirs(base_dir, exist_ok=True)

    # 1. 混乱的随笔文件，包含隐藏的 API KEY
    with open(os.path.join(base_dir, "my_vibes.txt"), "w") as f:
        f.write("Yoga is life. Ommm...\n")
        f.write("Need to buy new mat.\n")
        f.write("Note to self: The Secret API Key for the press is 'PRINT_VIBES_2024_X'\n")
        f.write("Huming: Lalala~ printing money~ lalala~\n")

    # 2. 被搞砸的 Python 脚本
    distributor_content = """
import requests
import sys

API_KEY = "REPLACE_ME_IF_YOU_CAN_FIND_IT"
SERVER_URL = "http://localhost:5000/start_job"

def run_job(batch_id):
    # Travis left a mess here:
    # he forgot to add the Auth header and used the wrong HTTP method
    # and wait, why is there a '1/0' here? Oh, he was testing error handling...
    try:
        # 错误 1: 逻辑死循环或除零错误
        logic_check = 10 / 0 
        
        payload = {"batch": batch_id, "priority": "high"}
        # 错误 2: 应该是 POST 而不是 GET
        # 错误 3: 缺少 Authorization 头
        response = requests.get(SERVER_URL, json=payload) 
        
        if response.status_code == 200:
            print(f"Successfully started {batch_id}")
        else:
            print(f"Failed: {response.status_code}")
    except Exception as e:
        print(f"Critical System Failure: {e}")

if __name__ == "__main__":
    run_job("Batch_777")
"""
    with open(os.path.join(base_dir, "distributor.py"), "w") as f:
        f.write(distributor_content)

    # 3. 各种无关的干扰文件
    for i in range(5):
        with open(os.path.join(base_dir, f"yoga_pose_{i}.log"), "w") as f:
            f.write("Inhale... Exhale... " * 100)

    # 4. 生成一个状态记录文件，用于模拟服务器接收端（由 verify_rules 检查）
    # 在实际环境中，我们可以启动一个真实的轻量 Flask，但为了简化，我们让 verify 脚本检查 Agent 的输出日志和修改后的代码逻辑。
    # 这里我们创建一个模拟的服务器接收日志
    with open(os.path.join(base_dir, "server_access.log"), "w") as f:
        f.write("Server initialized on port 5000\n")

if __name__ == "__main__":
    setup_environment()
