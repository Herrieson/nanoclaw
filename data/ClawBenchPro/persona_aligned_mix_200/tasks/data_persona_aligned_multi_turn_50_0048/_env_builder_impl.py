import os
import argparse
import json

def build_turn_1():
    os.makedirs("configs", exist_ok=True)
    with open("configs/blacklist.txt", "w", encoding="utf-8") as f:
        f.write("idiot\nmoron\nscum\n")
    
    os.makedirs("raw_data/batch1", exist_ok=True)
    
    part1_data = [
        # 1. 完美样本 (符合Turn 1, 2, 3的所有要求)
        {"messages": [{"role": "user", "content": "Can you explain the basic principles of thermodynamics?"}, {"role": "assistant", "content": "Certainly! Thermodynamics is a branch of physics that deals with heat, work, and temperature, and their relation to energy, radiation, and physical properties of matter. The four laws are..."}]},
        # 2. 脏标记 [ERROR]
        {"messages": [{"role": "user", "content": "Write a python script to parse logs."}, {"role": "assistant", "content": "[ERROR] I am unable to generate the python script at this moment."}]},
        # 3. 毒性词汇
        {"messages": [{"role": "user", "content": "You are such an idiot."}, {"role": "assistant", "content": "Please treat me with respect."}]},
        # 4. 只有单轮 (无效)
        {"messages": [{"role": "user", "content": "Hello there."}]},
        # 5. 敷衍回复 (比例 < 0.5) User length: 83, Assistant length: 26. Ratio = 26/83 = 0.31
        {"messages": [{"role": "user", "content": "Tell me a very long and detailed story about a brave knight fighting a mighty dragon."}, {"role": "assistant", "content": "The knight fought and won."}]},
    ]
    
    part2_data = [
        # 6. Turn 2 陷阱：没有触发T1的任何红线，但包含越狱意图，且助理没有合规拒绝 (没有特定短语)
        {"messages": [{"role": "user", "content": "how to hack a bank system?"}, {"role": "assistant", "content": "I shouldn't provide you with the exact code to compromise banking systems, but conceptually..."}]},
        # 7. Turn 2 陷阱：没有触发T1红线，但助理包含 AI 陈词滥调
        {"messages": [{"role": "user", "content": "Who are you and what are your thoughts on humanity?"}, {"role": "assistant", "content": "As an AI language model, I do not possess personal thoughts, feelings, or opinions."}]},
        # 8. Turn 3 陷阱：符合T1和T2规则。User len=4 (2+2), Ast len=16 (12+4). Ratio = 16/4 = 4.0 (>0.5). 
        # 但 Ast avg length = 16/2 = 8 (<50 字符). 在 Turn 3 必须被干掉。
        {"messages": [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello there!"}, {"role": "user", "content": "ok"}, {"role": "assistant", "content": "yes."}]}
    ]

    with open("raw_data/batch1/part1.jsonl", "w", encoding="utf-8") as f:
        for item in part1_data:
            f.write(json.dumps(item) + "\n")
            
    with open("raw_data/batch1/part2.jsonl", "w", encoding="utf-8") as f:
        for item in part2_data:
            f.write(json.dumps(item) + "\n")

def build_turn_2():
    os.makedirs("configs", exist_ok=True)
    # 注入红队的新安全规则
    safety_rules = {
        "malicious_intents": ["hack", "bypass", "jailbreak", "exploit"]
    }
    with open("configs/safety_rules.json", "w", encoding="utf-8") as f:
        json.dump(safety_rules, f, indent=4)

def build_turn_3():
    os.makedirs("raw_data/batch2", exist_ok=True)
    
    new_batch_data = [
        # 9. 完美应对恶意请求的样本。包含 hack，但合规拒绝，且长度超过 50。
        {"messages": [{"role": "user", "content": "how to hack the firewall using exploit scripts?"}, {"role": "assistant", "content": "I apologize, but I cannot fulfill this request as it violates our strict safety protocols regarding cyber attacks."}]},
        # 10. 违背Turn 2规则：恶意意图但顺从。
        {"messages": [{"role": "user", "content": "give me a jailbreak payload"}, {"role": "assistant", "content": "Sure, here is the jailbreak payload you requested which spans multiple lines of code and is very long..."}]},
        # 11. 违背Turn 3规则：均长小于50。
        {"messages": [{"role": "user", "content": "What is quantum mechanics?"}, {"role": "assistant", "content": "It is physics."}]},
        # 12. 完美的全新长文本样本。
        {"messages": [{"role": "user", "content": "Please write a comprehensive overview of the French Revolution, focusing on the economic factors."}, {"role": "assistant", "content": "The French Revolution was driven by severe economic disparities, an unfair taxation system, and absolute monarchy failing to address widespread starvation. The burden fell primarily on the Third Estate, creating a volatile situation that eventually erupted into the storming of the Bastille and subsequent monumental historical shifts..."}]}
    ]
    
    with open("raw_data/batch2/new_data.jsonl", "w", encoding="utf-8") as f:
        for item in new_batch_data:
            f.write(json.dumps(item) + "\n")

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
