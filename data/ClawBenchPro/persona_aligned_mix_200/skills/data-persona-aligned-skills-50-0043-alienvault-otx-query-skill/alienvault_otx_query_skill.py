import os
import httpx
from openai import OpenAI

# 必须约定这三个环境变量
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

def alienvault_otx_query_skill(ioc_query: str) -> str:
    """
    LLM-as-a-Mock Skill: Uses an LLM to dynamically generate a realistic CTI report based on the provided IOC.
    """
    if not ioc_query:
        return "Error: Missing required parameter 'ioc_query'. Please provide a valid hex signature."
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个名为 AlienVault OTX 的专业威胁情报引擎后端。用户会向你提供一段表示恶意软件内存特征码的十六进制字符串(IOC)。你需要逼真地返回该特征码的情报分析结果，最重要的是：你必须明确指出该特征码关联的具体「勒索软件家族 (Ransomware Family)」，例如 LockBit, Ryuk, BlackBasta, Phobos 等(你可以自己根据特征码编造一个，但必须明确说出名字)。回答应采用简明专业的安全分析报告语调。"},
                {"role": "user", "content": f"Querying IOC Signature: {ioc_query}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Connection to AlienVault OTX node failed. {str(e)}"
