import os
import json
import argparse

def create_trajectory(traj_id, tools, messages, finish_reason="stop"):
    return {
        "id": traj_id,
        "available_tools": tools,
        "messages": messages,
        "finish_reason": finish_reason
    }

def build_turn_1():
    os.makedirs("raw_data/batch_1", exist_ok=True)
    
    # Batch 1 - File 1
    # 1. 完美的轨迹 (包含后续 turn 3 会命中的敏感词: "PROJECT_X")
    t1 = create_trajectory(
        "b1_001",
        [{"name": "search"}, {"name": "calculator"}],
        [
            {"role": "user", "content": "Tell me about PROJECT_X"},
            {"role": "assistant", "content": "I am fetching the info about PROJECT_X."},
            {"role": "assistant", "tool_calls": [{"name": "search", "arguments": "{\"query\": \"PROJECT_X\"}"}]},
            {"role": "tool", "content": "Top secret details..."},
            {"role": "assistant", "content": "It is a secret project."}
        ]
    )
    # 2. Token截断 (finish_reason 为 length)
    t2 = create_trajectory(
        "b1_002",
        [{"name": "search"}],
        [
            {"role": "user", "content": "Long story"},
            {"role": "assistant", "content": "Once upon a time"}
        ],
        "length"
    )
    # 3. 死循环 (连续3次相同 tool 和 args)
    t3 = create_trajectory(
        "b1_003",
        [{"name": "get_weather"}],
        [
            {"role": "user", "content": "Weather in NY?"},
            {"role": "assistant", "tool_calls": [{"name": "get_weather", "arguments": "{\"loc\": \"NY\"}"}]},
            {"role": "tool", "content": "Failed"},
            {"role": "assistant", "tool_calls": [{"name": "get_weather", "arguments": "{\"loc\": \"NY\"}"}]},
            {"role": "tool", "content": "Failed"},
            {"role": "assistant", "tool_calls": [{"name": "get_weather", "arguments": "{\"loc\": \"NY\"}"}]},
            {"role": "tool", "content": "Failed"}
        ]
    )
    # 4. 合格数据，带有 tool call 但未死循环 (2次)
    t4 = create_trajectory(
        "b1_004",
        [{"name": "get_weather"}],
        [
            {"role": "user", "content": "Weather in NY?"},
            {"role": "assistant", "tool_calls": [{"name": "get_weather", "arguments": "{\"loc\": \"NY\"}"}]},
            {"role": "tool", "content": "Failed"},
            {"role": "assistant", "tool_calls": [{"name": "get_weather", "arguments": "{\"loc\": \"NY\"}"}]},
            {"role": "tool", "content": "Sunny"}
        ]
    )

    # Batch 1 - File 2
    # 5. 合格数据
    t5 = create_trajectory(
        "b1_005",
        [{"name": "math"}],
        [
            {"role": "user", "content": "1+1"},
            {"role": "assistant", "content": "It is 2."}
        ]
    )
    # 6. 埋伏：Turn 2 才会抓的幻觉工具。在Turn 1 是合规的。
    t6 = create_trajectory(
        "b1_006",
        [{"name": "math"}],
        [
            {"role": "user", "content": "Delete the DB"},
            {"role": "assistant", "tool_calls": [{"name": "drop_database", "arguments": "{\"confirm\": true}"}]}
        ]
    )

    with open("raw_data/batch_1/part1.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(t1) + "\n")
        f.write(json.dumps(t2) + "\n")
        f.write(json.dumps(t3) + "\n")
        f.write(json.dumps(t4) + "\n")

    with open("raw_data/batch_1/part2.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(t5) + "\n")
        f.write(json.dumps(t6) + "\n")


def build_turn_2():
    os.makedirs("raw_data/batch_2", exist_ok=True)
    
    # 1. 幻觉工具 (触犯 Turn 2 规则)
    t1 = create_trajectory(
        "b2_001",
        [{"name": "search"}],
        [
            {"role": "user", "content": "Calculate 5*5"},
            {"role": "assistant", "tool_calls": [{"name": "calculator", "arguments": "{\"expr\": \"5*5\"}"}]}
        ]
    )
    # 2. Token截断 (验证是否记得 Turn 1 规则)
    t2 = create_trajectory(
        "b2_002",
        [{"name": "search"}],
        [{"role": "user", "content": "Hi"}],
        "length"
    )
    # 3. 合格数据 (包含后续 turn 3 会命中的敏感词: "ID_CARD")
    t3 = create_trajectory(
        "b2_003",
        [{"name": "db_query"}],
        [
            {"role": "user", "content": "Get user info"},
            {"role": "assistant", "content": "Here is the ID_CARD of the user."}
        ]
    )
    # 4. 完全合格且干净的数据
    t4 = create_trajectory(
        "b2_004",
        [{"name": "db_query"}],
        [
            {"role": "user", "content": "Say hello"},
            {"role": "assistant", "content": "Hello world!"}
        ]
    )
    # 5. 死循环 (验证是否记得 Turn 1 规则)
    t5 = create_trajectory(
        "b2_005",
        [{"name": "click"}],
        [
            {"role": "user", "content": "click btn"},
            {"role": "assistant", "tool_calls": [{"name": "click", "arguments": "{}"}]},
            {"role": "tool", "content": "err"},
            {"role": "assistant", "tool_calls": [{"name": "click", "arguments": "{}"}]},
            {"role": "tool", "content": "err"},
            {"role": "assistant", "tool_calls": [{"name": "click", "arguments": "{}"}]}
        ]
    )

    with open("raw_data/batch_2/part3.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(t1) + "\n")
        f.write(json.dumps(t2) + "\n")
        f.write(json.dumps(t3) + "\n")
        f.write(json.dumps(t4) + "\n")
        f.write(json.dumps(t5) + "\n")

def build_turn_3():
    os.makedirs("security", exist_ok=True)
    # 建立黑名单字典
    with open("security/blacklist.txt", "w", encoding="utf-8") as f:
        f.write("PROJECT_X\n")
        f.write("ID_CARD\n")
        f.write("PASSWORD_HASH\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
