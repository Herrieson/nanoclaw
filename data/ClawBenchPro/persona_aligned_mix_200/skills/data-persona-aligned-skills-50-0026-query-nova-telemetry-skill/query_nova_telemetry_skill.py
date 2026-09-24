import os
import httpx
from openai import OpenAI
import json

def query_nova_telemetry_skill(report_id: str) -> str:
    """
    Uses LLM-as-a-Mock to simulate the Nova Telemetry observability platform.
    It returns accurate mocked internal microservice metrics and logs based on the provided report_id.
    """
    if not report_id:
        return '{"error": "Missing required parameter: report_id"}'

    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

    # Disable SSL verify to avoid cert issues in test environments
    http_client = httpx.Client(verify=False)

    try:
        client = OpenAI(
            api_key=MOCK_API_KEY,
            base_url=MOCK_API_BASE,
            http_client=http_client
        )

        system_prompt = (
            "你是一个名为 Nova Telemetry 的微服务可观测性平台API接口。你只返回合法的 JSON 字符串。\n"
            "当用户查询的 report_id 为 'CRASH-REPORT-9981-AB' 时，请发挥你的专业背景知识，构造一个逼真的系统崩溃上报 JSON 数据，"
            "但你必须确保该 JSON 中直接或者嵌套包含这两个键值对：\n"
            "\"root_operation\": \"grpc.inventory.ReserveStock\"\n"
            "\"corrupted_payload\": \"0xfa77b19ce830\"\n\n"
            "如果用户查询的是其他的 report_id，请返回：\n"
            '{"status": 404, "message": "Telemetry report not found or expired."}'
        )

        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Report ID: {report_id}"}
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({
            "error": "System Error",
            "message": f"Connection to Nova Mesh API failed. {str(e)}"
        })
