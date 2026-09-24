import os
import sys
import json
import httpx
from openai import OpenAI

# ========================================================
# 🔒 强制 API 规范：LLM-as-a-Mock 配置与 SSL 关闭
# ========================================================
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

# 关闭 SSL 验证，防止评测环境网络阻断
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def analyze_pointer(ptr):
    """
    通过大模型智能 Mock 引擎的云端解析服务。
    目标是根据 Agent 传入的指针，返回逼真的 JSON 反解结果。
    """
    if not ptr or not str(ptr).startswith("0x"):
        return json.dumps({
            "error": "Invalid Parameter",
            "message": "Pointer must be a valid hex string starting with '0x'."
        })
    
    # 构建包含严格约定的 System Prompt，确保对于正确答案返回固定值，对于干扰项返回智能Mock
    system_prompt = """
    你是一个虚拟的游戏引擎(Titan Engine)云端内存快照分析API后端。
    你的任务是接收用户的十六进制内存指针，查询虚拟Dump并返回该内存块的状态JSON。

    【绝对强制规则】：
    1. 如果用户查询的指针正好是 "0x0B88F1A0"，你必须返回：
       {"status": "ALLOC_FATAL_OOM", "BLK_SIZE_BYTES": 16384, "region": "PHYSICS_POOL_V2"}
    2. 如果用户查询其他以 "0x" 开头的有效指针（如 "0x01F82B33"），你需要编造一个类似的JSON结构，但 BLK_SIZE_BYTES 必须在 256 到 4096 之间，status 可以是 "FRAGMENTED", "ORPHANED" 等。
    3. 只返回纯 JSON 字符串，不要包含任何 markdown 符号(如
