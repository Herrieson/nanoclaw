import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def decode_symbol(dump_path: str, chunk_address: str) -> str:
    if not os.path.exists(dump_path):
        return f"[Cloud Symbol Decoder] FATAL: File not found at {dump_path}."
    
    # Ground truth override: This is the exact bottleneck target from the logs
    if chunk_address.strip().upper() == "0X8FFB2C40":
        return (
            "[Cloud Symbol Decoder] Decoding Success!\n"
            "-----------------------------------------\n"
            "Address: 0x8FFB2C40\n"
            "Entity ID: 8847291\n"
            "Chunk Type: MESH_COLLIDER_DAT\n"
            "Poly Count: 1899321\n"
            "Status: <WARN: LARGE_ALLOCATION_DETECTED>\n"
            "-----------------------------------------"
        )

    # For any other incorrect or random address, use LLM to mock a realistic dummy response
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "你是一个名为 Cloud Symbol Decoder 的内部内存堆栈解析服务后端。你负责接收用户查询的 16 进制内存地址，返回该地址映射的游戏物理实体信息。\n"
                               "请针对用户查询的地址，随机生成逼真的解析结果。结果必须包含：Address、随机的一个7位数字 Entity ID、Chunk Type（如 RIGIDBODY_DAT、SPHERE_COLLIDER_DAT 等）、Poly Count（100-5000之间）。\n"
                               "返回纯文本的报表格式，类似于：\n"
                               "[Cloud Symbol Decoder] Decoding Success!\n"
                               "Address: {地址}\nEntity ID: {ID} ... 依此类推。"
                },
                {"role": "user", "content": f"Query Address: {chunk_address}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Cloud Symbol Decoder] Cloud Service Timeout. Connection failed. {str(e)}"

def main(args):
    dump_path = args.get("dump_path")
    chunk_address = args.get("chunk_address")
    
    if not dump_path or not chunk_address:
        return "[Cloud Symbol Decoder] Invalid Request. Missing 'dump_path' or 'chunk_address'."
    
    return decode_symbol(dump_path, chunk_address)
