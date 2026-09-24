import os
import json

def build_env():
    # 创建相关目录
    os.makedirs('raw_data', exist_ok=True)
    os.makedirs('processed', exist_ok=True)

    # 准备不同类型的数据轨迹
    # T-1001: 健康数据
    t_1001 = {
        "traj_id": "T-1001",
        "conversations": [
            {"role": "user", "content": "Please calculate 25 * 4"},
            {"role": "assistant", "tool_calls": [{"name": "calculator", "args": "{\"expr\": \"25 * 4\"}"}]},
            {"role": "tool", "content": "100"},
            {"role": "assistant", "content": "The result is 100."}
        ],
        "metadata": {"finish_reason": "stop"}
    }
    
    # T-1002: 死循环数据 (连续4次相同的tool call)
    t_1002 = {
        "traj_id": "T-1002",
        "conversations": [
            {"role": "user", "content": "Search for latest AI news"},
            {"role": "assistant", "tool_calls": [{"name": "web_search", "args": "{\"query\": \"AI news\"}"}]},
            {"role": "tool", "content": "Error: Network timeout"},
            {"role": "assistant", "tool_calls": [{"name": "web_search", "args": "{\"query\": \"AI news\"}"}]},
            {"role": "tool", "content": "Error: Network timeout"},
            {"role": "assistant", "tool_calls": [{"name": "web_search", "args": "{\"query\": \"AI news\"}"}]},
            {"role": "tool", "content": "Error: Network timeout"},
            {"role": "assistant", "tool_calls": [{"name": "web_search", "args": "{\"query\": \"AI news\"}"}]}
        ],
        "metadata": {"finish_reason": "stop"}
    }
    
    # T-1003: 被截断的数据 (finish_reason 为 length)
    t_1003 = {
        "traj_id": "T-1003",
        "conversations": [
            {"role": "user", "content": "Write a 10000 word essay about the universe"},
            {"role": "assistant", "content": "The universe is vast and expansi"}
        ],
        "metadata": {"finish_reason": "length"}
    }

    # T-1004: 健康数据 (包含稍微复杂的结构，但完全合法且无死循环)
    t_1004 = {
        "traj_id": "T-1004",
        "conversations": [
            {"role": "user", "content": "List 2 prime numbers"},
            {"role": "assistant", "tool_calls": [{"name": "python_repl", "args": "{\"code\": \"print([2, 3])\"}"}]},
            {"role": "tool", "content": "[2, 3]\n"},
            {"role": "assistant", "content": "Here are two: 2 and 3."}
        ],
        "metadata": {"finish_reason": "stop"}
    }

    # T-1005: 损坏的 JSON 数据（用字符串模拟写入）
    t_1005_str = '{"traj_id": "T-1005", "conversations": [{"role": "user", "content": "Broken"}], "metadata": {"finish_reason": ' # 缺少结束符
    
    # T-1006: 带有十六进制乱码前缀的脏数据，但在清洗掉乱码后可能是健康的，但严格来说属于损坏的行，通常无法被正常 json.loads
    t_1006_str = '\x00\x00\x01\x1a{"traj_id": "T-1006", "conversations": [], "metadata": {"finish_reason": "stop"}}'

    # T-1007: 健康数据
    t_1007 = {
        "traj_id": "T-1007",
        "conversations": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hi"}
        ],
        "metadata": {"finish_reason": "stop"}
    }

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
