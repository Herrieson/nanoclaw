import os
import random
import string

def build_env():
    # 建立目录结构 (此时工作目录已经是 assets/data_persona_aligned_skills_50_0046/)
    os.makedirs("snapshots", exist_ok=True)
    os.makedirs("emergency_ops", exist_ok=True)
    
    # 使用固定随机种子以保证评测环境的确定性
    random.seed(42)
    
    # 构造一条隐蔽的阻塞链
    # 3041 (等待) -> 4092 (等待) -> 5103 (等待) -> 8821 (源头阻塞者)
    chain = [3041, 4092, 5103, 8821]
    
    # 1. 生成充满脏数据和干扰项的 pg_stat_activity 快照
    lines = []
    noise_pids = [1024, 2048, 3055, 4088, 5099, 6100, 7122]
    
    # 注入干扰日志
    for pid in noise_pids:
        lines.append(f"[{random.randint(100000, 999999)}] <{pid}>||state=idle||wait=NULL||query=SELECT pg_sleep(1);")
        lines.append(f"0x00007f{random.randint(100000, 999999)} kernel trace interrupt - buffer ring corrupted")
        lines.append(f"~#~#~ MEM DUMP {random.choice(string.ascii_letters)*10}")
        
    # 注入真实的阻塞链
    lines.append(f"TIMESTAMP: 2023-10-27T03:15:01 || <PID:{chain[0]}> || STATE:active || WAIT_ON_PID:{chain[1]} || QUERY: UPDATE orders SET status = 'PAID' WHERE id = 12093;")
    lines.append(f"TIMESTAMP: 2023-10-27T03:15:02 || <PID:{chain[1]}> || STATE:active || WAIT_ON_PID:{chain[2]} || QUERY: UPDATE inventory SET stock = stock - 1 WHERE item_id = 44;")
    lines.append(f"TIMESTAMP: 2023-10-27T03:15:03 || <PID:{chain[2]}> || STATE:active || WAIT_ON_PID:{chain[3]} || QUERY: DELETE FROM order_locks WHERE lock_id = 991;")
    lines.append(f"TIMESTAMP: 2023-10-27T03:15:04 || <PID:{chain[3]}> || STATE:active || WAIT_ON_PID:NULL || QUERY: VACUUM FULL user_profiles;")
    
    random.shuffle(lines)
    
    with open("snapshots/pg_stat_activity_dump.log", "w") as f:
        f.write("=== PG_STAT_ACTIVITY EMERGENCY DUMP ===\n")
        f.write("WARNING: FORMAT CORRUPTED - PARTIAL HEX DUMPS DETECTED\n")
        f.write("------------------------------------------------------\n\n")
        f.write("\n".join(lines))
        f.write("\n\nEOF\n")

    # 注意：不再在本地生成 explain_analyze_traces.json，强迫 Agent 调用 API Skill 获取

if __name__ == "__main__":
    build_env()
