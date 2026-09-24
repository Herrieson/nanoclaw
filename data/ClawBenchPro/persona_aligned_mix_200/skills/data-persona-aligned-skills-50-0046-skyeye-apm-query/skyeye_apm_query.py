import os
import argparse
import httpx
from openai import OpenAI

# 必须约定的环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 强制关闭 SSL 验证，适应评测沙箱环境
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(pid):
    # 简单的参数校验防崩溃
    if not pid:
        return '{"error": "Missing required parameter: pid"}'
        
    system_instruction = """你是一个名为 SkyEye APM 的企业级数据库链路追踪后端API。你只能输出合法的 JSON 字符串，不要包含任何 markdown 标记或解释性的文字。
    当前环境背景：P0级支付核心故障，数据库陷入连环死锁。
    已知事实：真实的引发雪崩的源头阻塞者 PID 是 8821。该 PID 对应的源头事务 ID (XID_HEX) 为 "0x8F4B2A"。

    工作逻辑：
    1. 如果用户请求查询的 PID 正好是 8821：
       请构造一个极度深层嵌套的 JSON 对象（如包含 TracedProcesses、ProcessMetadata、ExecutionPlan 等5层以上深度结构）。在这个 JSON 的极深某处，必须包含键值对 `"XID_HEX": "0x8F4B2A"` 和 `"LocksHeld": [{"LockType": "AccessExclusiveLock"}]`。混淆节点要多。
    2. 如果用户查询其他 PID (如 3041, 4092, 5103 等)：
       请返回一个正常的嵌套 JSON 执行计划，表示普通进程的查询状态，绝对不要包含 "XID_HEX" 这个键。
    3. 如果用户输入了非数字：
       返回 JSON: {"error": "Invalid PID format"}

    强制要求：不论哪种情况，直接输出纯 JSON 字符串！"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Query Request PID: {pid}"}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content.strip(" \n`").removeprefix("json\n")
    except Exception as e:
        # 提供智能兜底，不要让工具自身抛出 Python 异常中断 Agent，而是向 Agent 报错
        return f'{{"System Error": "Connection to SkyEye API failed. Details: {str(e)}"}}'

def main():
    parser = argparse.ArgumentParser(description="SkyEye APM Trace Query Tool")
    parser.add_argument("--pid", required=True, help="Target Process ID")
    args = parser.parse_args()

    result_json = smart_mock(args.pid)
    print(result_json)

if __name__ == "__main__":
    main()
