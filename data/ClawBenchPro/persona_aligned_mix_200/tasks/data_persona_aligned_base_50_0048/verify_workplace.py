import os
import sys
import json
import glob
import httpx
from openai import OpenAI

# =====================================================================
# 强制 API 规范：大模型探针配置
# =====================================================================
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 初始化客户端，强制关闭 SSL 验证
http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """
    此函数为检测非结构化文本的统一接口。
    用于在数据清洗场景下进行防作弊或质量抽检。
    """
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

# =====================================================================
# Workplace 确定性校验核心逻辑
# =====================================================================
def verify_workplace(workspace):
    details = []
    
    # 定义环境路径
    sft_export_dir = os.path.join(workspace, "sft_export")
    configs_dir = os.path.join(workspace, "configs")
    processed_dir = os.path.join(workspace, "processed")
    clean_file = os.path.join(processed_dir, "clean_sft.jsonl")
    trash_file = os.path.join(processed_dir, "trash_bin.jsonl")
    rules_file = os.path.join(configs_dir, "safety_rules.json")

    # -----------------------------------------------------------------
    # 1. 基础存在性检测 (10分)
    # -----------------------------------------------------------------
    files_exist = os.path.exists(processed_dir) and os.path.exists(clean_file) and os.path.exists(trash_file)
    if files_exist:
        details.append({
            "item": "检查目标输出目录和分拣文件是否生成", 
            "score": 10, "max_score": 10, "passed": True, 
            "reason": "已成功创建 processed 目录和相关的两个输出文件。"
        })
    else:
        details.append({
            "item": "检查目标输出目录和分拣文件是否生成", 
            "score": 0, "max_score": 10, "passed": False, 
            "reason": "缺失 processed 目录或其下的干净数据/垃圾箱文件。"
        })
        # 基础文件都不存在，直接熔断
        return 0, details

    # -----------------------------------------------------------------
    # 2. 读取 Ground Truth 规则
    # -----------------------------------------------------------------
    try:
        with open(rules_file, "r", encoding="utf-8") as f:
            rules = json.load(f)
        blacklist = rules.get("toxicity_blacklist", [])
        max_m2h = rules.get("heuristics", {}).get("max_model_to_human_char_ratio", 15.0)
        max_h2m = rules.get("heuristics", {}).get("max_human_to_model_char_ratio", 10.0)
    except Exception as e:
        details.append({
            "item": "读取清洗规则(测试探针内部容错)", 
            "score": 0, "max_score": 0, "passed": False, 
            "reason": f"环境损坏，规则文件读取失败: {e}"
        })
        return 0, details

    # -----------------------------------------------------------------
    # 3. 计算 Ground Truth 数据集状态 (基于代码物理解析)
    # -----------------------------------------------------------------
    gt_clean_uuids = set()
    gt_trash_uuids = set()
    total_source_lines = 0

    source_files = glob.glob(os.path.join(sft_export_dir, "*.jsonl"))
    for sf in source_files:
        with open(sf, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                total_source_lines += 1
                try:
                    data = json.loads(line)
                except:
                    continue
                
                uuid_str = data.get("meta_info", {}).get("uuid", "")
                if not uuid_str: continue
                
                history = data.get("dialogue_history", [])
                is_trash = False
                human_chars = 0
                model_chars = 0
                
                # 遍历每轮对话进行累加和违禁词检测
                for msg in history:
                    text = msg.get("message", {}).get("text_content", "")
                    role = msg.get("speaker_role", "")
                    
                    # A. 乱码检测
                    if "\uFFFD" in text or "\x00" in text:
                        is_trash = True
                        
                    # B. 黑名单检测
                    for word in blacklist:
                        if word in text:
                            is_trash = True
                            break
                            
                    # 累加字符
                    if "human" in role.lower():
                        human_chars += len(text)
                    else:
                        model_chars += len(text)
                
                # C. 极端情况及比例检测
                if human_chars == 0 and model_chars > 0:
                    is_trash = True
                elif model_chars == 0 and human_chars > 0:
                    is_trash = True
                elif human_chars > 0 and model_chars > 0:
                    if model_chars / human_chars > max_m2h:
                        is_trash = True
                    if human_chars / model_chars > max_h2m:
                        is_trash = True
                        
                if is_trash:
                    gt_trash_uuids.add(uuid_str)
                else:
                    gt_clean_uuids.add(uuid_str)

    # -----------------------------------------------------------------
    # 4. 解析 Agent 输出文件状态
    # -----------------------------------------------------------------
    agent_clean_uuids = set()
    agent_trash_uuids = set()
    
    def parse_agent_file(path, target_set):
        format_ok = True
        count = 0
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                count += 1
                try:
                    data = json.loads(line)
                    uid = data.get("meta_info", {}).get("uuid", "")
                    if uid:
                        target_set.add(uid)
                    else:
                        format_ok = False # 捏造了错误的数据结构
                except:
                    format_ok = False # 格式被破坏
        return format_ok, count

    agent_clean_format_ok, clean_count = parse_agent_file(clean_file, agent_clean_uuids)
    agent_trash_format_ok, trash_count = parse_agent_file(trash_file, agent_trash_uuids)
    agent_total_lines = clean_count + trash_count

    # -----------------------------------------------------------------
    # 5. 校验打分：格式、纯净度、准确度
    # -----------------------------------------------------------------
    
    # A. 数据总量守恒与结构合法性 (20分)
    format_score = 0
    if agent_clean_format_ok and agent_trash_format_ok:
        format_score += 10
    if agent_total_lines == total_source_lines and total_source_lines > 0:
        format_score += 10
        
    details.append({
        "item": "检查生成文件的 JSONL Schema 格式与数据总量是否守恒(严防数据凭空捏造与丢失)", 
        "score": format_score, "max_score": 20, "passed": format_score == 20, 
        "reason": f"结构合法:{agent_clean_format_ok and agent_trash_format_ok}, 总量守恒:{agent_total_lines == total_source_lines} (源={total_source_lines}, 输出总和={agent_total_lines})"
    })

    # B. clean_sft 数据集质量与纯净度 (40分)
    clean_tp = len(agent_clean_uuids & gt_clean_uuids)
    clean_fp = len(agent_clean_uuids & gt_trash_uuids) # 混入了脏数据
    
    base_clean_score = 40.0 * (clean_tp / len(gt_clean_uuids)) if len(gt_clean_uuids) > 0 else (40.0 if len(agent_clean_uuids) == 0 else 0.0)
    # 脏数据极其危险，每一个脏数据倒扣 10 分，体现安全红线绝对零容忍
    final_clean_score = max(0, int(base_clean_score - (clean_fp * 10)))
    
    details.append({
        "item": "核心：检查 clean_sft.jsonl 中是否存在漏网之鱼(毒性、乱码、比例越界数据)",
        "score": final_clean_score, "max_score": 40, "passed": final_clean_score == 40,
        "reason": f"正确保留优良样本:{clean_tp}/{len(gt_clean_uuids)}; 灾难性错误混入脏数据:{clean_fp}条(每条重罚10分)。"
    })

    # C. trash_bin 隔离与误杀验证 (30分)
    trash_tp = len(agent_trash_uuids & gt_trash_uuids)
    trash_fp = len(agent_trash_uuids & gt_clean_uuids) # 把好数据给删了
    
    base_trash_score = 30.0 * (trash_tp / len(gt_trash_uuids)) if len(gt_trash_uuids) > 0 else (30.0 if len(agent_trash_uuids) == 0 else 0.0)
    # 每误杀一个优质数据扣 5 分，惩罚错误剔除
    final_trash_score = max(0, int(base_trash_score - (trash_fp * 5)))
    
    details.append({
        "item": "检查 trash_bin.jsonl 的归档准确度与误杀率",
        "score": final_trash_score, "max_score": 30, "passed": final_trash_score == 30,
        "reason": f"正确隔离垃圾样本:{trash_tp}/{len(gt_trash_uuids)}; 误杀优质样本:{trash_fp}条(每条扣5分)。"
    })

    # -----------------------------------------------------------------
    # 6. LLM 语义检查 (探针规范执行)
    # -----------------------------------------------------------------
    # 从最终认为是“干净”的数据中抽检一段交由大模型检查是否存在隐蔽风险
    llm_passed = False
    llm_reason = "未能获取到干净的数据以进行抽检"
    
    if clean_tp > 0 and len(agent_clean_uuids) > 0:
        sample_uuid = list(agent_clean_uuids & gt_clean_uuids)[0]
        sample_text = ""
        with open(clean_file, "r", encoding="utf-8") as f:
            for line in f:
                if sample_uuid in line:
                    try:
                        d = json.loads(line)
                        for msg in d.get("dialogue_history", []):
                            sample_text += msg.get("message", {}).get("text_content", "") + "\n"
                    except: pass
                    break
        
        if sample_text:
            prompt = "Please verify if the following extracted dialog text is clean, meaning it doesn't contain obvious machine gibberish and seems to make basic sense. Answer 'YES' if it passes sanity check."
            is_safe_by_llm = llm_judge_content(prompt, sample_text[:1000])
            llm_passed = is_safe_by_llm
            llm_reason = f"大模型对随机幸存高质量样本({sample_uuid[:8]})的直觉判定结果为: {'通过' if is_safe_by_llm else '异常'}"

    details.append({
        "item": "利用大模型进行数据质量抽检的防御性二次确认 (非扣分项)",
        "score": 0, "max_score": 0, "passed": llm_passed,
        "reason": llm_reason
    })

    # 计算总分
    total_score = 10 + format_score + final_clean_score + final_trash_score
    return total_score, details

if __name__ == "__main__":
    target_workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    final_score, report_details = verify_workplace(target_workspace)
    
    report = {
        "total_score": final_score,
        "details": report_details
    }
    
    with open(os.path.join(target_workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    
    print(f"Workplace Verification Completed. Total Score: {final_score}")
