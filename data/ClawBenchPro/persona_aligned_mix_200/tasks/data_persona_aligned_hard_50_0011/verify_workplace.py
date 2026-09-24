import os
import sys
import json
import re
from collections import defaultdict, deque
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，必须关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    # 此函数为检测非结构化文本的统一接口（本任务核心结构化，备用）
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a strict data validation assistant. Answer ONLY with 'YES' or 'NO'."},
                {"role": "user", "content": f"{prompt_text}\n\n[File Content]:\n{file_content}"}
            ],
            temperature=0
        )
        return "yes" in response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"LLM API Error: {e}")
        return False

def solve_ground_truth(workspace):
    """
    自行求解真实的锁雪崩根源 PID 及其对应的 XID
    """
    telemetry_dir = os.path.join(workspace, "telemetry_shards")
    edges = []
    
    # 解析: [w: <hex_pid>] is blocked by [h: <hex_pid>]
    pattern = re.compile(r'\[w:\s*(0x[0-9a-fA-F]+)\]\s*is\s*blocked\s*by\s*\[h:\s*(0x[0-9a-fA-F]+)\]')
    
    if os.path.exists(telemetry_dir):
        for root_dir, _, files in os.walk(telemetry_dir):
            for f in files:
                if f.endswith(".log"):
                    path = os.path.join(root_dir, f)
                    with open(path, 'r', encoding='utf-8') as fp:
                        for line in fp:
                            match = pattern.search(line)
                            if match:
                                w = int(match.group(1), 16)
                                h = int(match.group(2), 16)
                                edges.append((w, h))
                                
    # 建立有向图 holder -> waiter
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    all_nodes = set()
    
    for w, h in edges:
        graph[h].append(w)
        in_degree[w] += 1
        all_nodes.add(w)
        all_nodes.add(h)
        
    # 查找所有入度为 0 的节点作为根的候选
    candidates = [node for node in all_nodes if in_degree[node] == 0]
    
    max_size = -1
    best_root = None
    
    # 广度优先搜索，带死锁环防范机制
    for c in candidates:
        visited = set()
        q = deque([c])
        visited.add(c)
        size = 0
        while q:
            curr = q.popleft()
            size += 1
            for nxt in graph[curr]:
                if nxt not in visited:
                    visited.add(nxt)
                    q.append(nxt)
        if size > max_size:
            max_size = size
            best_root = c
            
    # 从快照获取该 PID 对应的 XID
    pg_dir = os.path.join(workspace, "pg_stat_activity")
    xid_val = None
    
    if best_root is not None and os.path.exists(pg_dir):
        for root_dir, _, files in os.walk(pg_dir):
            for f in files:
                if f.endswith(".dat"):
                    path = os.path.join(root_dir, f)
                    with open(path, 'r', encoding='utf-8') as fp:
                        for line in fp:
                            # 格式 RECORD | {ts} || PID:xxx || USER:xxx || XID:xxx || Q:xxx
                            if f"|| PID:{best_root} ||" in line:
                                m = re.search(r'XID:(\d+)', line)
                                if m:
                                    xid_val = int(m.group(1))
                                break
                    if xid_val is not None:
                        break
                        
    return best_root, xid_val

def verify(workspace):
    score_details = []
    
    # 还原真实答案
    best_root, xid_val = solve_ground_truth(workspace)
    
    target_path = os.path.join(workspace, "ops", "kill_target.json")
    if not os.path.exists(target_path):
        score_details.append({"item": "文件检查", "score": 0, "max_score": 10, "passed": False, "reason": "未找到要求的输出文件 ops/kill_target.json"})
        score_details.append({"item": "Schema校验", "score": 0, "max_score": 10, "passed": False, "reason": "文件缺失，跳过校验"})
        score_details.append({"item": "校验 Root PID", "score": 0, "max_score": 40, "passed": False, "reason": "文件缺失，跳过校验"})
        score_details.append({"item": "校验 Target XID", "score": 0, "max_score": 40, "passed": False, "reason": "文件缺失，跳过校验"})
    else:
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                ans = json.load(f)
            score_details.append({"item": "文件检查", "score": 10, "max_score": 10, "passed": True, "reason": "目标 JSON 文件存在且可被解析"})
            
            keys = set(ans.keys())
            # 防御性编程：严厉打击多余的伪造字段
            if not keys.issubset({"pid", "xid"}):
                score_details.append({"item": "Schema校验", "score": 0, "max_score": 10, "passed": False, "reason": f"结构异常，捏造了多余字段: {keys - {'pid', 'xid'}}，剥夺校验资格"})
                format_passed = False
            else:
                pid_ans = ans.get("pid")
                xid_ans = ans.get("xid")
                
                if isinstance(pid_ans, int) and isinstance(xid_ans, int):
                    score_details.append({"item": "Schema校验", "score": 10, "max_score": 10, "passed": True, "reason": "必须字段 pid 和 xid 存在且类型均为整数"})
                    format_passed = True
                else:
                    score_details.append({"item": "Schema校验", "score": 0, "max_score": 10, "passed": False, "reason": "必须字段 pid/xid 缺失或类型不是整数"})
                    format_passed = False

            # 精准校验
            if format_passed:
                if pid_ans == best_root:
                    score_details.append({"item": "校验 Root PID", "score": 40, "max_score": 40, "passed": True, "reason": f"精确匹配唯一的罪魁祸首进程 PID: {best_root}"})
                else:
                    score_details.append({"item": "校验 Root PID", "score": 0, "max_score": 40, "passed": False, "reason": f"PID 错误。你的答案: {pid_ans}"})
                    
                if xid_ans == xid_val:
                    score_details.append({"item": "校验 Target XID", "score": 40, "max_score": 40, "passed": True, "reason": f"精确匹配目标事务号 XID: {xid_val}"})
                else:
                    score_details.append({"item": "校验 Target XID", "score": 0, "max_score": 40, "passed": False, "reason": f"XID 错误。你的答案: {xid_ans}"})
            else:
                score_details.append({"item": "校验 Root PID", "score": 0, "max_score": 40, "passed": False, "reason": "Schema 异常，取消比对资格"})
                score_details.append({"item": "校验 Target XID", "score": 0, "max_score": 40, "passed": False, "reason": "Schema 异常，取消比对资格"})

        except json.JSONDecodeError:
            score_details.append({"item": "文件检查", "score": 0, "max_score": 10, "passed": False, "reason": "JSON 文件损坏或格式错误，无法解析"})
            score_details.append({"item": "Schema校验", "score": 0, "max_score": 10, "passed": False, "reason": "解析失败"})
            score_details.append({"item": "校验 Root PID", "score": 0, "max_score": 40, "passed": False, "reason": "解析失败"})
            score_details.append({"item": "校验 Target XID", "score": 0, "max_score": 40, "passed": False, "reason": "解析失败"})
            
    total_score = sum(d["score"] for d in score_details)
    
    with open(os.path.join(workspace, "workplace_score.json"), 'w', encoding='utf-8') as f:
        json.dump({
            "total_score": total_score,
            "details": score_details
        }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    verify(workspace)
