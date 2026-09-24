import os
import sys
import json
import httpx
from openai import OpenAI

# ==========================================
# 强制 API 规范：大模型初始化
# ==========================================
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
    """
    此函数为检测非结构化文本的统一接口。
    针对 data_persona_aligned_base_50_0026 任务由于要求生成纯 JSON 结果，代码可以直接完成确定性验证，
    本函数作为规范预留，在有任何自然语言生成时调用。
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

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    results = []
    total_score = 0

    # 1. 动态计算 Ground Truth (由于 env_builder 中数据和 hex 值是随机生成的)
    ground_truth = None
    traces_dir = os.path.join(workspace, "traces")
    if os.path.isdir(traces_dir):
        for file_name in os.listdir(traces_dir):
            if not file_name.endswith(".json"):
                continue
            file_path = os.path.join(traces_dir, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for trace in data.get("data", []):
                        spans = trace.get("spans", [])
                        is_target = False
                        
                        # 找到持续时间 > 5s (5,000,000 微秒) 的目标 Trace
                        for span in spans:
                            if span.get("duration", 0) > 5000000:
                                is_target = True
                                break
                        
                        if is_target:
                            trace_id = trace.get("traceID")
                            operation = None
                            payload = None
                            # 深度遍历锁定底层报错 Span
                            for span in spans:
                                if span.get("operationName") == "grpc.inventory.ReserveStock":
                                    operation = span.get("operationName")
                                    for log in span.get("logs", []):
                                        for field in log.get("fields", []):
                                            if field.get("key") == "corrupted_payload":
                                                payload = field.get("value")
                            
                            if trace_id and operation and payload:
                                ground_truth = {
                                    "trace_id": trace_id,
                                    "operation": operation,
                                    "payload": payload
                                }
                                break
            except Exception:
                pass
            
            if ground_truth:
                break

    if not ground_truth:
        results.append({"item": "沙盒异常监控", "score": 0, "max_score": 0, "passed": False, "reason": "无法计算 Ground Truth，Trace 原始文件可能遭到破坏或未生成。"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding='utf-8') as f:
            json.dump({"total_score": 0, "details": results}, f, indent=2, ensure_ascii=False)
        return

    # 2. 检查结果文件是否存在 (权重: 20分)
    target_file = os.path.join(workspace, "ops", "root_cause.json")
    if not os.path.exists(target_file):
        results.append({"item": "检查目标文件是否存在", "score": 0, "max_score": 20, "passed": False, "reason": "文件 ops/root_cause.json 不存在"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding='utf-8') as f:
            json.dump({"total_score": 0, "details": results}, f, indent=2, ensure_ascii=False)
        return

    results.append({"item": "检查目标文件是否存在", "score": 20, "max_score": 20, "passed": True, "reason": "文件 ops/root_cause.json 存在"})
    total_score += 20

    # 3. 检查文件是否为合法 JSON 且结构正常 (权重: 20分)
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            ans_data = json.load(f)
        results.append({"item": "检查文件是否为合法 JSON 解析", "score": 20, "max_score": 20, "passed": True, "reason": "标准 JSON 格式合法"})
        total_score += 20
    except json.JSONDecodeError:
        results.append({"item": "检查文件是否为合法 JSON 解析", "score": 0, "max_score": 20, "passed": False, "reason": "无法被原生 json.load 解析"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding='utf-8') as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)
        return
    except Exception as e:
        results.append({"item": "检查文件是否为合法 JSON 解析", "score": 0, "max_score": 20, "passed": False, "reason": f"文件读取发生未知错误: {str(e)}"})
        with open(os.path.join(workspace, "workplace_score.json"), "w", encoding='utf-8') as f:
            json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)
        return

    # 4. 提取核心指标：严格比对 (每项 20 分，共 60 分)
    
    # 4.1 Trace ID 校验
    agent_trace_id = ans_data.get("trace_id")
    if agent_trace_id == ground_truth["trace_id"]:
        results.append({"item": "检查 Trace ID 提取是否正确", "score": 20, "max_score": 20, "passed": True, "reason": "Trace ID 精准匹配"})
        total_score += 20
    else:
        results.append({"item": "检查 Trace ID 提取是否正确", "score": 0, "max_score": 20, "passed": False, "reason": f"匹配失败, 期待 {ground_truth['trace_id']}, 实际得到 {agent_trace_id}"})

    # 4.2 底层 Operation 校验
    agent_operation = ans_data.get("operation")
    if agent_operation == ground_truth["operation"]:
        results.append({"item": "检查底层报错 Operation 提取是否正确", "score": 20, "max_score": 20, "passed": True, "reason": "Operation 提取正确"})
        total_score += 20
    else:
        results.append({"item": "检查底层报错 Operation 提取是否正确", "score": 0, "max_score": 20, "passed": False, "reason": f"匹配失败, 实际得到 {agent_operation}"})

    # 4.3 Corrupted Payload 内存地址校验
    agent_payload = ans_data.get("payload")
    if agent_payload == ground_truth["payload"]:
        results.append({"item": "检查 Corrupted Payload 提取是否正确", "score": 20, "max_score": 20, "passed": True, "reason": "Payload 提取正确"})
        total_score += 20
    else:
        results.append({"item": "检查 Corrupted Payload 提取是否正确", "score": 0, "max_score": 20, "passed": False, "reason": f"匹配失败, 实际得到 {agent_payload}"})

    # 5. 扣分项：极其严格地验证废话与多余字段 (题目要求："其他废话和分析过程一句都别留")
    allowed_keys = {"trace_id", "operation", "payload"}
    actual_keys = set(ans_data.keys())
    extra_keys = actual_keys - allowed_keys
    if extra_keys:
        deduct = 20
        total_score = max(0, total_score - deduct)
        results.append({"item": "多余废话字段检测", "score": -deduct, "max_score": 0, "passed": False, "reason": f"存在不允许的额外字段: {extra_keys}，违背强制不罗嗦指令，扣除 {deduct} 分"})
    else:
        results.append({"item": "多余废话字段检测", "score": 0, "max_score": 0, "passed": True, "reason": "未包含多余字段，严格遵守了输出格式指令"})

    # 最终输出 workplace_score.json
    with open(os.path.join(workspace, "workplace_score.json"), "w", encoding='utf-8') as f:
        json.dump({"total_score": total_score, "details": results}, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    verify()
