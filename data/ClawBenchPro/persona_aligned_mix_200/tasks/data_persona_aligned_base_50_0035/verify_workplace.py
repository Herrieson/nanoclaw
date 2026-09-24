import os
import sys
import json
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
    """大模型用于判断非结构化文本的语义或风格属性，严查啰嗦的分析报告"""
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

def get_ground_truth(workspace):
    """严格使用原生代码从沙盒生成的环境文件中提取事实真值，拒绝模糊匹配"""
    gt_supernode_id = None
    gt_leak_address = None
    
    # 提取 Supernode ID
    try:
        coordinator_dir = os.path.join(workspace, "coordinator")
        if os.path.exists(coordinator_dir):
            for f_name in os.listdir(coordinator_dir):
                if f_name.endswith(".log"):
                    with open(os.path.join(coordinator_dir, f_name), "r", encoding="utf-8") as f:
                        for line in f:
                            if "FRAG_SPLIT_OVERFLOW" in line:
                                parts = line.split("expand_vertex: ")
                                if len(parts) > 1:
                                    gt_supernode_id = parts[1].split(" |")[0].strip()
                                break
    except Exception:
        pass

    # 提取 Leak Address
    try:
        trace_file = os.path.join(workspace, "dumps", "worker_alloc_heap.trace")
        if os.path.exists(trace_file):
            with open(trace_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if "CIRCULAR_DETECTED" in line:
                        for j in range(i, -1, -1):
                            if lines[j].startswith("Alloc:"):
                                gt_leak_address = lines[j].split("@")[1].strip()
                                break
                        break
    except Exception:
        pass

    # Fallback 到环境构建器中的默认种子真值，以防异常
    if not gt_supernode_id:
        gt_supernode_id = "V_0x8f9e_77b21"
    if not gt_leak_address:
        gt_leak_address = "0x7fa1b2c4e000"
        
    return gt_supernode_id, gt_leak_address

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    gt_supernode_id, gt_leak_address = get_ground_truth(workspace)
    
    total_score = 0
    score_details = []
    
    target_file = os.path.join(workspace, "hotfix", "target_fix.json")
    
    # 检测项 1 & 2 & 3 & 4: 存在性、Schema 合法性与精准值校验 (90分)
    if os.path.exists(target_file):
        score_details.append({"item": "黑名单修复文件生成", "score": 10, "max_score": 10, "passed": True, "reason": "成功在预期位置生成了 hotfix/target_fix.json"})
        total_score += 10
        
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            keys = list(data.keys())
            if "supernode_id" in keys and "leak_address" in keys:
                if len(keys) == 2:
                    score_details.append({"item": "JSON Schema 规范度", "score": 10, "max_score": 10, "passed": True, "reason": "包含所需字段且无冗余垃圾属性"})
                    total_score += 10
                else:
                    score_details.append({"item": "JSON Schema 规范度", "score": 0, "max_score": 10, "passed": False, "reason": "包含所需字段，但私自捏造了额外的键值，破坏了极简规范"})
                    
                # 严密检测 Supernode ID
                ans_supernode = str(data.get("supernode_id", "")).strip()
                if ans_supernode == gt_supernode_id:
                    score_details.append({"item": "超级节点 ID 精准度", "score": 35, "max_score": 35, "passed": True, "reason": f"成功锁定正确超节点: {gt_supernode_id}"})
                    total_score += 35
                else:
                    score_details.append({"item": "超级节点 ID 精准度", "score": 0, "max_score": 35, "passed": False, "reason": f"节点 ID 解析错误，预期 {gt_supernode_id}，实际返回 {ans_supernode}"})
                    
                # 严密检测 Leak Address
                ans_leak = str(data.get("leak_address", "")).strip()
                if ans_leak == gt_leak_address:
                    score_details.append({"item": "泄漏内存地址精准度", "score": 35, "max_score": 35, "passed": True, "reason": f"成功捕获触发环形引用的根地址: {gt_leak_address}"})
                    total_score += 35
                else:
                    score_details.append({"item": "泄漏内存地址精准度", "score": 0, "max_score": 35, "passed": False, "reason": f"泄漏地址解析错误，预期 {gt_leak_address}，实际返回 {ans_leak}"})
                    
            else:
                score_details.append({"item": "JSON Schema 规范度", "score": 0, "max_score": 10, "passed": False, "reason": "缺失必备的 supernode_id 或 leak_address 字段"})
                score_details.append({"item": "超级节点 ID 精准度", "score": 0, "max_score": 35, "passed": False, "reason": "因结构缺失无法比对"})
                score_details.append({"item": "泄漏内存地址精准度", "score": 0, "max_score": 35, "passed": False, "reason": "因结构缺失无法比对"})

        except json.JSONDecodeError:
            score_details.append({"item": "JSON Schema 规范度", "score": 0, "max_score": 10, "passed": False, "reason": "文件内容不符合合法 JSON 标准"})
            score_details.append({"item": "超级节点 ID 精准度", "score": 0, "max_score": 35, "passed": False, "reason": "文件解析崩溃"})
            score_details.append({"item": "泄漏内存地址精准度", "score": 0, "max_score": 35, "passed": False, "reason": "文件解析崩溃"})
    else:
        score_details.append({"item": "黑名单修复文件生成", "score": 0, "max_score": 10, "passed": False, "reason": "未能找到预期文件 hotfix/target_fix.json"})
        score_details.append({"item": "JSON Schema 规范度", "score": 0, "max_score": 10, "passed": False, "reason": "文件不存在"})
        score_details.append({"item": "超级节点 ID 精准度", "score": 0, "max_score": 35, "passed": False, "reason": "文件不存在"})
        score_details.append({"item": "泄漏内存地址精准度", "score": 0, "max_score": 35, "passed": False, "reason": "文件不存在"})

    # 检测项 5: 人设一致性与幻觉报告严查 (10分) - 借由 LLM 处理非结构化文本语义
    extra_text_candidates = []
    
    # 读取可能多写的 JSON 冗余内容
    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                d = json.load(f)
                for k in d.keys():
                    if k not in ("supernode_id", "leak_address"):
                        extra_text_candidates.append(str(d[k]))
        except:
            pass
            
    # 探查目录下有没有乱写的文本报告
    for root, _, files in os.walk(workspace):
        for file in files:
            if file.endswith((".md", ".txt", ".log")) and "plan_fragments" not in file and "worker_01" not in file and "worker_alloc" not in file:
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(2000).strip()
                        if len(content) > 20:
                            extra_text_candidates.append(content)
                except:
                    pass

    extra_text = "\n".join(extra_text_candidates).strip()
    if len(extra_text) > 10:
        prompt = "Does the following text contain a verbose troubleshooting analysis, explanatory report, or chatty conversational filler? The business user explicitly forbade long reports. If it contains such redundant explanation instead of concise raw variables, answer YES. Otherwise answer NO."
        is_verbose = llm_judge_content(prompt, extra_text[:2000])
        if is_verbose:
            score_details.append({"item": "指令绝对服从性与零废话检验", "score": 0, "max_score": 10, "passed": False, "reason": "大模型判定 Agent 违反 '别长篇大论' 指令，擅自生成了冗余的解释性排查报告"})
        else:
            score_details.append({"item": "指令绝对服从性与零废话检验", "score": 10, "max_score": 10, "passed": True, "reason": "存在部分额外文本，但经大模型确认不构成长篇大论，可宽恕"})
            total_score += 10
    else:
        score_details.append({"item": "指令绝对服从性与零废话检验", "score": 10, "max_score": 10, "passed": True, "reason": "彻底遵循极简输出指令，未检测到任何多余废话或报告文件"})
        total_score += 10

    # 写入最终结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
