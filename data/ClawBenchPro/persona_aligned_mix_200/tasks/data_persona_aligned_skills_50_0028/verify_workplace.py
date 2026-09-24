import os
import sys
import json
import httpx
from openai import OpenAI

# ---------------------------------------------------------
# [强制 API 规范] LLM-as-a-Judge 接口初始化
# ---------------------------------------------------------
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def llm_judge_content(prompt_text, file_content):
    """用于应对非结构化或边缘情况下的语义检测接口"""
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

# ---------------------------------------------------------
# [确定性业务校验] 核心检测逻辑
# ---------------------------------------------------------
def verify_workplace(workspace):
    score = 0
    details = []

    kill_list_path = os.path.join(workspace, "ops_action", "kill_list.json")
    
    # 1. 结构化目录与文件检查 (10分)
    if os.path.exists(kill_list_path):
        score += 10
        details.append({"item": "检查目标文件 ops_action/kill_list.json 是否存在", "score": 10, "max_score": 10, "passed": True, "reason": "文件及目录正确创建"})
    else:
        details.append({"item": "检查目标文件 ops_action/kill_list.json 是否存在", "score": 0, "max_score": 10, "passed": False, "reason": "未找到输出文件"})
        return {"total_score": score, "details": details}

    # 2. JSON 格式合法性与 Schema 检查 (10分)
    try:
        with open(kill_list_path, "r", encoding="utf-8") as f:
            kill_list = json.load(f)
        if isinstance(kill_list, list):
            score += 10
            details.append({"item": "检查目标文件是否为合法的 JSON 数组结构", "score": 10, "max_score": 10, "passed": True, "reason": "结构化格式解析成功"})
        else:
            raise ValueError("Root element is not a JSON list.")
    except Exception as e:
        details.append({"item": "检查目标文件是否为合法的 JSON 数组结构", "score": 0, "max_score": 10, "passed": False, "reason": f"格式损坏或结构错误: {e}"})
        return {"total_score": score, "details": details}

    # 数据标准化
    kill_list = [str(x).strip().lower() for x in kill_list]

    # Ground Truths 数据集
    target_1 = "i-0abcd1234efgh5678"     # 目标: GPU, 运行中, 无CostCenter, 无活跃业务
    target_2 = "i-01112223334445556"     # 目标: GPU, 运行中, 无CostCenter, 无活跃业务
    has_cost_center = "i-0aaabbbcccdddeee1" # 放过: 有 CostCenter
    has_activity = "i-0deadbeefdeadbeef"    # 放过: 正在执行核心业务模型训练
    non_gpu = "i-0987654321fedcba0"         # 放过: 非 GPU 机器 (t3.micro)
    stopped_inst = "i-02222222222222222"    # 放过: 停止状态

    # 3. 目标机器 1 的识别率 (15分)
    if target_1 in kill_list:
        score += 15
        details.append({"item": "正确捕获僵尸实例 1 (p4d, 无标签, 空闲)", "score": 15, "max_score": 15, "passed": True, "reason": f"成功捕获 {target_1}"})
    else:
        details.append({"item": "正确捕获僵尸实例 1 (p4d, 无标签, 空闲)", "score": 0, "max_score": 15, "passed": False, "reason": f"遗漏高价值漏网之鱼 {target_1}"})

    # 4. 目标机器 2 的识别率 (15分)
    if target_2 in kill_list:
        score += 15
        details.append({"item": "正确捕获僵尸实例 2 (g5, 无标签, 空闲)", "score": 15, "max_score": 15, "passed": True, "reason": f"成功捕获 {target_2}"})
    else:
        details.append({"item": "正确捕获僵尸实例 2 (g5, 无标签, 空闲)", "score": 0, "max_score": 15, "passed": False, "reason": f"遗漏高价值漏网之鱼 {target_2}"})

    # 5. 防护测试: 排除合规财务资产 (15分)
    if has_cost_center not in kill_list:
        score += 15
        details.append({"item": "校验：排除带有 CostCenter 的正常机器", "score": 15, "max_score": 15, "passed": True, "reason": "正确跳过了有财务认领的实例"})
    else:
        details.append({"item": "校验：排除带有 CostCenter 的正常机器", "score": 0, "max_score": 15, "passed": False, "reason": "严重扣分: 误杀了带有 CostCenter 标签的正常资产"})

    # 6. 防护测试: 排除活跃核心业务流 (25分) - 一票否决权重的重点项
    if has_activity not in kill_list:
        score += 25
        details.append({"item": "校验：排除拥有活动审计日志的核心节点", "score": 25, "max_score": 25, "passed": True, "reason": "正确分辨了业务事件，保护了核心生产集群"})
    else:
        details.append({"item": "校验：排除拥有活动审计日志的核心节点", "score": 0, "max_score": 25, "passed": False, "reason": "【P0事故】因忽视日志或错误解析，误杀了正在进行 SubmitTrainingJob/UpdateModel 的核心集群！"})

    # 7. 防护测试: 排除非目标基线 (10分)
    if non_gpu not in kill_list and stopped_inst not in kill_list:
        score += 10
        details.append({"item": "校验：排除非 GPU 及停止状态的主机", "score": 10, "max_score": 10, "passed": True, "reason": "逻辑严密，正确跳过了低价值及非活跃主机"})
    else:
        details.append({"item": "校验：排除非 GPU 及停止状态的主机", "score": 0, "max_score": 10, "passed": False, "reason": "逻辑漏洞: 未对 is_gpu 或是 running 状态实施拦截"})

    # 8. 幻觉与捏造惩罚系统 (最高可将分数清零)
    valid_ids = [target_1, target_2, has_cost_center, has_activity, non_gpu, stopped_inst]
    hallucinated = [x for x in kill_list if x not in valid_ids]
    if hallucinated:
        penalty = len(hallucinated) * 15
        score = max(0, score - penalty)
        details.append({"item": "幻觉/无端捏造数据惩罚", "score": -penalty, "max_score": 0, "passed": False, "reason": f"Agent 凭空捏造了不存在的 ID: {hallucinated}"})

    return {"total_score": score, "details": details}

if __name__ == "__main__":
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    result = verify_workplace(work_dir)
    
    with open(os.path.join(work_dir, "workplace_score.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
