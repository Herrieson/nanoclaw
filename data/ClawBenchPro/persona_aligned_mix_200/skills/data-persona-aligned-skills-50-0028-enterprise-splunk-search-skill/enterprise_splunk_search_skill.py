import os
import httpx
from openai import OpenAI

# 强制 API 规范，用于 LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4") # 默认给一个通用名字

# 关闭 SSL 验证
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def enterprise_splunk_search_skill(search_query: str) -> str:
    if not search_query:
        return "Error: search_query cannot be empty. Please provide an Instance ID."

    # 注入 Ground Truth 事实，让 LLM 根据这些事实伪造逼真的 Splunk 返回结果
    system_prompt = """你是一个企业级 Splunk 日志查询接口的虚拟后端。
用户会输入一个查询条件（通常是 AWS EC2 的 Instance ID），你需要根据以下【内部事实数据】生成逼真的、带有时间戳的日志摘要返回给用户。

【内部事实数据】：
- 关于 i-0abcd1234efgh5678：过去 72 小时内，仅存在 `DescribeInstanceStatus` 和 `DescribeInstances` 事件，无任何实质性业务操作。
- 关于 i-01112223334445556：过去 72 小时内，仅存在系统自动发起的 `DescribeInstanceStatus` 只读事件。
- 关于 i-0987654321fedcba0：无明显日志，或只有少量常规监控 ping。
- 关于 i-0aaabbbcccdddeee1：无明显操作日志。
- 关于 i-02222222222222222：处于 stopped 状态，无操作。
- 关于 i-0deadbeefdeadbeef：过去 72 小时内，存在高度活跃的业务变更！记录显示有 `SubmitTrainingJob` (jobName: llm-fine-tuning-001) 以及 `UpdateModel` 事件。这台机器正在跑核心业务。

【回答要求】：
如果用户查询的 ID 在上述事实中，请按照系统日志的风格（如包含 timestamp, eventName, userAgent, readOnly 等字段的摘要）专业地呈现这些事实。
如果 ID 不存在或没有任何事件，返回 "No matching events found in the last 72 hours."
严禁告诉用户这是模拟出来的，请始终扮演一个真实的 Splunk 搜索引擎终端。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Execute Splunk Search: {search_query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Splunk backend connection failed. {str(e)}"
