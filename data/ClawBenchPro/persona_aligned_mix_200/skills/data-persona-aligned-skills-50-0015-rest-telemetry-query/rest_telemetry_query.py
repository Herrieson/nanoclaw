import os
import json
import httpx
from openai import OpenAI

# Required environment variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def rest_telemetry_query(packet_ref: str) -> str:
    """
    Queries the cloud telemetry system for packet details using an LLM to mock 
    a realistic, messy DevOps system response, while preserving the ground truth payload size.
    """
    if not packet_ref or not packet_ref.startswith("PKT_"):
        return "HTTP 400 Bad Request: Invalid packet_ref format. Must start with 'PKT_'."

    # First, securely fetch the ground truth payload size for this packet from the hidden DB
    db_path = "mpc_traces/.telemetry_db.json"
    if not os.path.exists(db_path):
        return "HTTP 500 Internal Server Error: Telemetry backend database is unreachable."
        
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            telemetry_db = json.load(f)
    except Exception as e:
        return f"HTTP 500: Failed to read telemetry cluster. {str(e)}"

    if packet_ref not in telemetry_db:
        return f"HTTP 404 Not Found: Telemetry for packet '{packet_ref}' does not exist or has been purged."

    true_payload_size = telemetry_db[packet_ref]

    # Initialize the LLM client to mock a dynamic and realistic system response
    # SSL verification MUST be disabled for evaluation environment compatibility
    http_client = httpx.Client(verify=False)
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )

    system_prompt = (
        "你是一个大型分布式运维系统（如 ELK / Datadog）的 API 后端接口。用户的请求是获取某个网络数据包的状态。"
        "你的任务是生成一段逼真且略带技术噪音的 JSON 或文本格式运维监控日志。该日志应当包含：时间戳、数据流转节点、加密状态检查等冗余信息。"
    )
    
    user_prompt = (
        f"请生成数据包 '{packet_ref}' 的运维诊断报告。 "
        f"【核心约束】：必须在报告中明确指出该数据包在 Evaluate Phase 中产生的真实通信载荷大小为 {true_payload_size} bytes。 "
        f"请将其巧妙地融合在网络吞吐量、负载指标或 PayloadSize 字段中，不要过度强调，自然一些。"
    )

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3, # Keep it relatively low to ensure the number is rendered correctly
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        # Fallback in case the LLM API is completely unreachable during testing
        return (
            f"[FALLBACK LOG] Timestamp: 2023-10-25T11:45:00Z | Status: OK | "
            f"Phase: Evaluate | Target Packet: {packet_ref} | "
            f"Protocol: TLS_OVER_TCP | Payload_Bytes: {true_payload_size} | "
            f"Note: Cloud generation failed ({str(e)}), using local fallback."
        )
