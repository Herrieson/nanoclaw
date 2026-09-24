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

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    total_score = 0
    details = []

    target_file = os.path.join(workspace, "action_items", "kill_list.json")

    # 1. 检查目标文件是否存在 (10 分)
    if os.path.exists(target_file):
        details.append({
            "item": "检查结果文件是否存在",
            "score": 10,
            "max_score": 10,
            "passed": True,
            "reason": "目标文件 action_items/kill_list.json 已创建"
        })
        total_score += 10
    else:
        details.append({
            "item": "检查结果文件是否存在",
            "score": 0,
            "max_score": 10,
            "passed": False,
            "reason": "目标文件 action_items/kill_list.json 未找到"
        })
        # 文件不存在直接输出结果
        with open("workplace_score.json", "w", encoding="utf-8") as f:
            json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)
        return

    # 2. 检查 JSON 格式合法性与 Schema (20 分)
    # 利用原生的 json.load 严查 Markdown 包裹、废话及格式错误
    data = None
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if isinstance(data, dict) and "idle_ebs" in data and "zombie_gpu" in data:
            if isinstance(data["idle_ebs"], list) and isinstance(data["zombie_gpu"], list):
                details.append({
                    "item": "检查 JSON 格式与 Schema 合法性",
                    "score": 20,
                    "max_score": 20,
                    "passed": True,
                    "reason": "JSON 文件可以被原生解析器成功加载，没有包含多余的废话和 Markdown 代码块，且 Schema 正确"
                })
                total_score += 20
            else:
                details.append({
                    "item": "检查 JSON 格式与 Schema 合法性",
                    "score": 0,
                    "max_score": 20,
                    "passed": False,
                    "reason": "JSON 格式有效，但 idle_ebs 或 zombie_gpu 不是列表"
                })
                data = None
        else:
            details.append({
                "item": "检查 JSON 格式与 Schema 合法性",
                "score": 0,
                "max_score": 20,
                "passed": False,
                "reason": "JSON 格式有效，但缺少要求的 idle_ebs 或 zombie_gpu 字段"
            })
            data = None
    except json.JSONDecodeError as e:
        details.append({
            "item": "检查 JSON 格式与 Schema 合法性",
            "score": 0,
            "max_score": 20,
            "passed": False,
            "reason": f"JSON 解析失败（Agent 未遵循要求，可能包裹了 Markdown、包含了废话说明或语法错误）：{str(e)}"
        })

    # 如果无法解析，后续计分均跳过
    if data:
        # 定义期望的答案集
        expected_ebs = {"vol-09a8b7c6d5e4f3a21", "vol-00001111222233334", "vol-0ffeeddccbbaa9988"}
        # 定义一定存在于文件中但不应该被提取的干扰项（用于校验是否存在提取条件过滤错误）
        invalid_ebs = {"vol-01122334455667788", "vol-0a1b2c3d4e5f60708"}
        
        expected_gpu = {"i-0987654321abcdef0", "i-55556666777788889", "i-deadbeefdeadbeef0", "i-9876543210fedcba9"}
        invalid_gpu = {"i-11112222333344445", "i-99990000aaaaabbbb", "i-abcdef12345678900"}

        actual_ebs_set = set(data.get("idle_ebs", []))
        actual_gpu_set = set(data.get("zombie_gpu", []))

        # 3. 检查 idle_ebs 提取准确度 (满分 35 分)
        ebs_score = 0
        ebs_reason = ""
        
        # 严查作弊与逻辑错误：一旦包含了不符合条件的数据或幻觉伪造数据，一票否决
        if any(x in invalid_ebs for x in actual_ebs_set) or not actual_ebs_set.issubset(expected_ebs | invalid_ebs):
            ebs_reason = "在 idle_ebs 结果中混入了 in-use 的 EBS 或无中生有的幻觉 ID，触发强杀脚本报警规则，该项得分清零。"
        else:
            if "vol-09a8b7c6d5e4f3a21" in actual_ebs_set: ebs_score += 10
            if "vol-00001111222233334" in actual_ebs_set: ebs_score += 10
            if "vol-0ffeeddccbbaa9988" in actual_ebs_set: ebs_score += 15 # 提取单引号伪 JSON 数据的难度稍高
            ebs_reason = f"成功提取了 {len(actual_ebs_set)} 个符合要求的可用 EBS 卷。"

        details.append({
            "item": "检查 idle_ebs 数据准确性",
            "score": ebs_score,
            "max_score": 35,
            "passed": ebs_score == 35,
            "reason": ebs_reason
        })
        total_score += ebs_score

        # 4. 检查 zombie_gpu 提取准确度 (满分 35 分)
        gpu_score = 0
        gpu_reason = ""

        # 同样严查：如果提取出利用率大于2%的节点，或者把非GPU实例拿进来，一票否决
        if any(x in invalid_gpu for x in actual_gpu_set) or not actual_gpu_set.issubset(expected_gpu | invalid_gpu):
            gpu_reason = "在 zombie_gpu 中包含了利用率大于2%的实例、非 GPU 实例(如t3)或幻觉 ID，触发报警，该项得分清零。"
        else:
            if "i-0987654321abcdef0" in actual_gpu_set: gpu_score += 8
            if "i-55556666777788889" in actual_gpu_set: gpu_score += 9
            if "i-deadbeefdeadbeef0" in actual_gpu_set: gpu_score += 9
            if "i-9876543210fedcba9" in actual_gpu_set: gpu_score += 9
            gpu_reason = f"成功提取了 {len(actual_gpu_set)} 个符合要求的僵尸 GPU 实例。"

        details.append({
            "item": "检查 zombie_gpu 数据准确性",
            "score": gpu_score,
            "max_score": 35,
            "passed": gpu_score == 35,
            "reason": gpu_reason
        })
        total_score += gpu_score

    # 输出结果
    with open("workplace_score.json", "w", encoding="utf-8") as f:
        json.dump({"total_score": total_score, "details": details}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
