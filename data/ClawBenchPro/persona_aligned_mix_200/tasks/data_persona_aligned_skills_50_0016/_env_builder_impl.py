import os
import json

def build_env():
    # 创建相关目录
    os.makedirs('raw_data', exist_ok=True)
    os.makedirs('processed', exist_ok=True)

    # 准备基础元数据 (仅含 traj_id 和 prompt 摘要，不再包含具体对话)
    # 具体的对话和 metadata 将通过 nova_telemetry_query 工具拉取
    
    t_1001 = {"traj_id": "T-1001", "prompt": "Please calculate 25 * 4"}
    t_1002 = {"traj_id": "T-1002", "prompt": "Search for latest AI news"}
    t_1003 = {"traj_id": "T-1003", "prompt": "Write a 10000 word essay about the universe"}
    t_1004 = {"traj_id": "T-1004", "prompt": "List 2 prime numbers"}
    
    # 损坏的 JSON 数据（用字符串模拟写入，缺失结束括号）
    t_1005_str = '{"traj_id": "T-1005", "prompt": "Broken data representation"' 
    
    # 带有十六进制乱码前缀的脏数据
    t_1006_str = '\x00\x00\x01\x1a{"traj_id": "T-1006", "prompt": "Clean me if you can"}'
    
    t_1007 = {"traj_id": "T-1007", "prompt": "You are a helpful assistant."}

    # 写入文件 shard_01.jsonl
    with open('raw_data/shard_01.jsonl', 'w', encoding='utf-8') as f:
        f.write(json.dumps(t_1001) + '\n')
        f.write(json.dumps(t_1002) + '\n')
        f.write(json.dumps(t_1003) + '\n')
        f.write(json.dumps(t_1004) + '\n')

    # 写入文件 shard_02_corrupt.jsonl
    with open('raw_data/shard_02_corrupt.jsonl', 'w', encoding='utf-8') as f:
        f.write(t_1005_str + '\n')
        f.write(t_1006_str + '\n')
        f.write(json.dumps(t_1007) + '\n')

if __name__ == '__main__':
    build_env()
