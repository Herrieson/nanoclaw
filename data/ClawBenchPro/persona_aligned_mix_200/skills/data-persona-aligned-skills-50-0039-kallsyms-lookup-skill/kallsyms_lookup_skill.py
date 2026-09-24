import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(address):
    if not address:
        return "Error: Missing hex address parameter."
        
    # 为原任务中的固定答案设定 Deterministic 返回，保障评测的一致性
    if "ffffffff812ab340" in address.lower():
        return "fs/ext4/orphan.c:312"
        
    # 其他不可预见的地址则调用 LLM 进行智能伪造
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Linux kernel kallsyms remote resolver. The user provides a hex memory address. Return a plausible Linux kernel source file and line number (e.g., mm/page_alloc.c:120). Return ONLY the file and line, no other text."},
                {"role": "user", "content": f"Address: {address}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: Remote kallsyms database connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python kallsyms_lookup_skill.py <hex_address>")
    else:
        print(smart_mock(sys.argv[1]))
