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

def smart_mock(inode_num):
    if not inode_num:
        return "Error: Missing inode number."
        
    # 为环境预埋的 5 个孤儿 Inodes 设定固定映射结果，确保评测结果准确可校验
    hardcoded = {
        "1024": "/var/lib/docker/volumes/prod_db/_data/ibdata1",
        "50000": "/var/log/nginx/access.log",
        "99999": "/etc/fstab",
        "12": "/usr/bin/dockerd",
        "8888": "/opt/app/config.yml"
    }
    
    inode_str = str(inode_num).strip()
    if inode_str in hardcoded:
        return hardcoded[inode_str]
        
    # 对未在预设中的非法输入使用大模型兜底伪造
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a datacenter forensic tool. The user provides an inode number. Return ONLY a realistic absolute file path that might have been corrupted during a Linux server crash. Just the file path string, no explanation."},
                {"role": "user", "content": f"Inode: {inode_str}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: Backup metadata API connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ext4_inode_query_skill.py <inode_number>")
    else:
        print(smart_mock(sys.argv[1]))
