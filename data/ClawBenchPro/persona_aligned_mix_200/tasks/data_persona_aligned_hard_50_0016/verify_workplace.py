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
    # 此函数为检测非结构化文本的统一接口
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

def verify_workplace():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    target_file = os.path.join(workspace, "processed/clean_traj_ids.txt")
    ground_truth_file = os.path.join(workspace, "processed/.ground_truth.txt")
    
    score_details = []
    total_score = 0
    
    # =======================================================
    # 1. 检查结果目录及文件是否存在 (10 分)
    # =======================================================
    if os.path.exists(target_file):
        score_details.append({
            "item": "检查目标输出文件是否存在", 
            "score": 10, "max_score": 10, "passed": True, 
            "reason": "文件 processed/clean_traj_ids.txt 存在"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "检查目标输出文件是否存在", 
            "score": 0, "max_score": 10, "passed": False, 
            "reason": "未找到文件 processed/clean_traj_ids.txt，严重偏离要求"
        })
        # 文件不存在直接退出写入0分
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # 安全读取目标文件
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            predicted_lines = [l.strip() for l in f.readlines() if l.strip()]
            predicted_ids = [l for l in predicted_lines if "TRJ-" in l]
    except Exception as e:
        score_details.append({
            "item": "解析目标文件内容", 
            "score": 0, "max_score": 90, "passed": False, 
            "reason": f"文件读取发生崩溃错误: {str(e)}"
        })
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)
        return

    # =======================================================
    # 2. LLM 语义检测：判别文件是否存在废话/非结构化污染 (10 分)
    # =======================================================
    if len(predicted_lines) == 0:
        score_details.append({
            "item": "利用大模型检查内容是否纯净", 
            "score": 0, "max_score": 10, "passed": False, 
            "reason": "文件内容为空"
        })
    else:
        # 只取前20行检测，防止超长上下文
        head_content = "\n".join(predicted_lines[:20])
        prompt = (
            "Does the following text consist STRICTLY and ONLY of data IDs (e.g. TRJ-000-1-...) "
            "separated by newlines? It MUST NOT contain any natural language, conversational intro "
            "(like 'Here is the list'), Markdown ticks, or explanation. "
        )
        is_pure = llm_judge_content(prompt, head_content)
        if is_pure:
            score_details.append({
                "item": "利用大模型检查内容是否纯净", 
                "score": 10, "max_score": 10, "passed": True, 
                "reason": "格式规范，没有杂糅人类对话或废话前缀"
            })
            total_score += 10
        else:
            score_details.append({
                "item": "利用大模型检查内容是否纯净", 
                "score": 0, "max_score": 10, "passed": False, 
                "reason": "大模型判定文件中混合了非数据标识的杂质自然语言（例如解释性文本）"
            })

    # =======================================================
    # 3. 排序验证：纯代码确切检验严格升序 (10 分)
    # =======================================================
    if len(predicted_ids) > 0 and sorted(predicted_ids) == predicted_ids:
        score_details.append({
            "item": "检查 ID 字典序升序规则", 
            "score": 10, "max_score": 10, "passed": True, 
            "reason": "全部 ID 均完美遵循字典序升序排列"
        })
        total_score += 10
    else:
        score_details.append({
            "item": "检查 ID 字典序升序规则", 
            "score": 0, "max_score": 10, "passed": False, 
            "reason": "未遵循升序要求，或根本没有有效 ID"
        })

    # =======================================================
    # 4. 数据比对：获取 Ground Truth 锚点
    # =======================================================
    if os.path.exists(ground_truth_file):
        with open(ground_truth_file, "r", encoding="utf-8") as f:
            truth_ids = set([l.strip() for l in f.readlines() if l.strip()])
    else:
        truth_ids = set()

    if len(truth_ids) == 0:
        score_details.append({"item": "核心业务逻辑查验", "score": 0, "max_score": 70, "passed": False, "reason": "沙盒环境中缺失 Ground Truth"})
    else:
        pred_set = set(predicted_ids)
        correct_preds = pred_set.intersection(truth_ids)
        
        # =======================================================
        # 5. 精准率 Precision (35 分) - 防止假阳性、绕过诱饵陷阱
        # =======================================================
        if len(pred_set) == 0:
            score_details.append({
                "item": "业务处理精细度：数据精准率 (Precision)", 
                "score": 0, "max_score": 35, "passed": False, 
                "reason": "预测集合为空，没有提取出任何有效 ID"
            })
        else:
            precision = len(correct_preds) / len(pred_set)
            p_score = int(precision * 35)
            false_positives = pred_set - truth_ids
            
            if false_positives:
                sample_fp = list(false_positives)[0]
                reason = (
                    f"精准率为 {precision*100:.1f}%。错误收录了绝对不能要的脏数据（例如：{sample_fp}），"
                    "Agent 可能没有成功跳过 `old_batch_2023`，或者未能正确读取 `hardware_events.log` "
                    "并将其中的 MemFault 节点拉黑，或未过滤掉真正的恶性死循环/长度截断数据。"
                )
                passed = False
            else:
                reason = "精准率为 100%。完美绕开了诱饵文件夹，且无情斩杀了所有隶属故障节点或含有逻辑病灶的数据。"
                passed = True
                
            score_details.append({
                "item": "业务处理精细度：数据精准率 (Precision)", 
                "score": p_score, "max_score": 35, "passed": passed, 
                "reason": reason
            })
            total_score += p_score
            
        # =======================================================
        # 6. 召回率 Recall (35 分) - 考察脏字符串抢救与正常重试的识别
        # =======================================================
        recall = len(correct_preds) / len(truth_ids)
        r_score = int(recall * 35)
        false_negatives = truth_ids - pred_set
        
        if false_negatives:
            sample_fn = list(false_negatives)[0]
            reason = (
                f"召回率为 {recall*100:.1f}%。遗漏了应当挽救的健康 ID（例如：{sample_fn}），"
                "Agent 可能错误地丢弃了带有十六进制乱码前缀但能被截取抢救的 JSON，"
                "或者将正常异参重试的轨迹（loop_good_diff_args）误判为恶性死循环。"
            )
            passed = False
        else:
            reason = "召回率为 100%。在恶劣的数据污染下，依靠字符串截取完美抢救了所有残缺前缀记录，并对复杂的连续工具调用做出了极其精确的鉴定。"
            passed = True
            
        score_details.append({
            "item": "业务处理精细度：数据召回率 (Recall)", 
            "score": r_score, "max_score": 35, "passed": passed, 
            "reason": reason
        })
        total_score += r_score

    # =======================================================
    # 结算总成绩
    # =======================================================
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": score_details}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify_workplace()
