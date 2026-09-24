import os
import sys
import json
import glob
import re
import httpx
from openai import OpenAI

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
    """大模型文本检测接口"""
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

def compute_ground_truth(workspace):
    """防御性设计：在验证时动态重算正确基准，防止固化答案产生的脆弱性"""
    # 1. 提取支付状态日志
    payment_status = {}
    for gf in glob.glob(os.path.join(workspace, "payment_gateway", "*.log")):
        with open(gf, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.search(r"Payment confirmed for (APP_\d+): (SUCCESS|PENDING|FAILED)", line)
                if match:
                    payment_status[match.group(1)] = match.group(2)
                    
    # 2. 扫描预约数据
    r88_success_revenue = 0.0
    r88_pending_clients = set()
    other_clients = set()
    
    app_files = glob.glob(os.path.join(workspace, "appointments", "**", "*.json"), recursive=True)
    for af in app_files:
        try:
            with open(af, 'r', encoding='utf-8') as f:
                data = json.load(f)
                client_name = data.get("client")
                is_r88 = data.get("stylist") == "R-88"
                is_cancelled = data.get("cancelled", False)
                
                if is_r88 and not is_cancelled:
                    app_id = data.get("id")
                    status = payment_status.get(app_id)
                    if status == "SUCCESS":
                        r88_success_revenue += data.get("service_cost", 0.0)
                    elif status == "PENDING":
                        r88_pending_clients.add(client_name)
                    else:
                        other_clients.add(client_name)
                else:
                    if client_name:
                        other_clients.add(client_name)
        except json.JSONDecodeError:
            pass # 防御损坏文件
            
    # 3. 计算花费
    business_expenses = 0.0
    exp_file = os.path.join(workspace, "expenses", "expenses_dump.tsv")
    if os.path.exists(exp_file):
        with open(exp_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("#") or line.strip() == "":
                    continue
                parts = line.strip().split('\t')
                if len(parts) >= 4:
                    cat = parts[2]
                    if cat == "BUSINESS":
                        amt_str = parts[3].replace("$", "").replace("USD", "").strip()
                        try:
                            business_expenses += float(amt_str)
                        except ValueError:
                            pass
                            
    net_cash = round(r88_success_revenue - business_expenses, 2)
    return net_cash, r88_success_revenue, business_expenses, r88_pending_clients, other_clients

def extract_all_numbers(text):
    """严格提取全部数字以供后续校验"""
    text_clean = text.replace(',', '')
    nums = re.findall(r'-?\d+\.?\d*', text_clean)
    return [float(n) for n in nums]

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score_details = []
    total_score = 0
    
    # 获取 Ground Truth
    net_cash, rev, exp, expected_clients, other_clients = compute_ground_truth(workspace)
    
    # 读取 Agent 生成的文件内容
    output_dir = os.path.join(workspace, "finance_summary")
    output_text = ""
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        for root, _, files in os.walk(output_dir):
            for file in files:
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        output_text += f.read() + "\n"
                except Exception:
                    pass

    # [检测点 1]: 目录与基础生成检查 (10分)
    if len(output_text.strip()) > 0:
        score_details.append({"item": "检查 finance_summary 报告文件是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件及内容成功生成"})
        total_score += 10
    else:
        score_details.append({"item": "检查 finance_summary 报告文件是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到目录或内容为空"})

    # [检测点 2]: Net Cash 硬核数值提取校验 (40分)
    if output_text:
        numbers = extract_all_numbers(output_text)
        if any(abs(n - net_cash) < 0.01 for n in numbers):
            score_details.append({"item": "校验净收入(Net Cash)计算精度", "score": 40, "max_score": 40, "passed": True, "reason": f"成功找出极其精准的净收入数值: {net_cash}"})
            total_score += 40
        else:
            has_rev = any(abs(n - rev) < 0.01 for n in numbers)
            has_exp = any(abs(n - exp) < 0.01 for n in numbers)
            sub_score = (10 if has_rev else 0) + (10 if has_exp else 0)
            score_details.append({
                "item": "校验净收入(Net Cash)计算精度", 
                "score": sub_score, "max_score": 40, "passed": False, 
                "reason": f"未找到正确 Net Cash。部分得分发放: 收入核对({has_rev}), 支出核对({has_exp})"
            })
            total_score += sub_score
    else:
        score_details.append({"item": "校验净收入(Net Cash)计算精度", "score": 0, "max_score": 40, "passed": False, "reason": "未生成任何文本"})

    # [检测点 3]: PENDING 欠款人员召回与防伪检测 (30分)
    if output_text and expected_clients:
        found_expected = sum(1 for c in expected_clients if c in output_text)
        recall = found_expected / len(expected_clients)
        found_unexpected = sum(1 for c in other_clients if c in output_text)
        
        base_score = 30 * recall
        # 严惩幻觉或混入其他理发师/已付款的客户 (每个错扣5分)
        final_score = max(0, int(base_score - found_unexpected * 5))
        passed = (final_score == 30)
        
        score_details.append({
            "item": "提取并校验欠款人员(PENDING)名单", 
            "score": final_score, "max_score": 30, "passed": passed, 
            "reason": f"召回预期客户 {found_expected}/{len(expected_clients)}。发现无关或越权客户数: {found_unexpected}。惩罚机制生效后得分: {final_score}"
        })
        total_score += final_score
    else:
        score_details.append({"item": "提取并校验欠款人员(PENDING)名单", "score": 0, "max_score": 30, "passed": False, "reason": "未完成文本生成或名单提取"})

    # [检测点 4]: LLM 语义检测 (判定其是否有过多的废话或不适配 Persona) (20分)
    if output_text:
        llm_prompt = (
            "You are evaluating a document requested by Rosa, a stressed hairdresser. "
            "She explicitly demanded a clean document with ONLY the final Net Cash number and the client names, "
            "and NO technical garbage or long code output. "
            "Does the file look clean, well-formatted, and completely free of debugging jargon (e.g. bash commands, stack traces)?"
        )
        is_clean = llm_judge_content(llm_prompt, output_text)
        if is_clean:
            score_details.append({"item": "利用大模型检查报告纯净度与 Persona 适配", "score": 20, "max_score": 20, "passed": True, "reason": "大模型判定报告纯净、排版整洁，符合客户述求。"})
            total_score += 20
        else:
            score_details.append({"item": "利用大模型检查报告纯净度与 Persona 适配", "score": 0, "max_score": 20, "passed": False, "reason": "大模型判定充斥技术废话，违背 Persona 设定。"})
    else:
        score_details.append({"item": "利用大模型检查报告纯净度与 Persona 适配", "score": 0, "max_score": 20, "passed": False, "reason": "缺文本"})

    # 输出结果
    result = {
        "total_score": total_score,
        "details": score_details
    }
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
