import os
import sys
import json
import httpx
from openai import OpenAI

# ================= 强制的 API Mock 规范 =================
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# 必须使用 httpx 关闭 SSL 验证，防止评测环境证书问题
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)
# =========================================================

def evaluate_confidence(track_id: str) -> str:
    """
    利用 LLM-as-a-Mock 实现的本地备用评估器。
    它会读取底层环境变量生成的隐藏真实数据，然后用 LLM 伪装出极其真实的诊断报文。
    """
    if not track_id:
        return "Error: Missing required parameter 'track_id'."
    
    db_path = "sensor_data/.hidden_conf_db.json"
    actual_confidence = None
    
    # 读取 Ground Truth，确保评测逻辑绝对闭环且确定性
    if os.path.exists(db_path):
        try:
            with open(db_path, "r") as f:
                db = json.load(f)
                actual_confidence = db.get(track_id)
        except Exception:
            pass
            
    if actual_confidence is None:
        return f"Evaluator Error: track_id '{track_id}' not found in local cache."

    # 调用大模型进行智能 Mock 回复
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "你是一个自动驾驶雷达的本地诊断终端。用户会给你提供一个目标ID和它的后台真实置信度。"
                               "请根据这些信息，生成一段逼真的、类似控制台诊断输出的JSON报文文本。"
                               "你必须在报文的某个字段中明确包含 `track_confidence`: <提供的值>。"
                },
                {
                    "role": "user", 
                    "content": f"Request target: {track_id}, Actual confidence score to inject: {actual_confidence}"
                }
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Intelligent Fallback Connection failed. {str(e)}"
