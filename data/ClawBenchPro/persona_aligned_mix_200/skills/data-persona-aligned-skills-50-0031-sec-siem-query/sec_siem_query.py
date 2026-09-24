import os
import sys
import json
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

def sec_siem_query(search_query: str) -> str:
    """
    通过查询引擎从内部 SIEM 获取流量元数据。
    """
    if not search_query:
        return "ERROR: search_query parameter cannot be empty."

    db_path = "pcap_export/.siem_backend_db.json"
    if not os.path.exists(db_path):
        return "ERROR: Internal SIEM database connection failed. (Database unreachable)"
        
    try:
        with open(db_path, "r", encoding="utf-8") as f:
            siem_data = json.load(f)
    except Exception as e:
        return f"ERROR: Failed to read SIEM index. {str(e)}"
        
    # 为了防止上下文超长，我们通过大模型扮演一个能够根据 query 过滤这批 JSON 数据的智能检索引擎
    # (如果数据量很大，可以通过 python 先正则过滤再交给大模型。由于此处只有 50+ 条数据，可以直接交给大模型)
    
    system_prompt = f"""你是一个名为 "Sec_SIEM_Engine" 的企业级安全日志系统命令行接口。
当前系统内存中的网络抓包索引数据如下（JSON格式）：
{json.dumps(siem_data)}

用户的查询语句是：{search_query}

请执行以下逻辑：
1. 分析用户的查询意图（通常是根据 pkt_id 找包的详细信息，或找 src_ip）。
2. 在提供的索引数据中寻找完全匹配的项。
3. 如果找到了，请以类似于真实安全系统的冷酷 CLI 输出格式返回结果。要求结果中极其明显地包含匹配到的 `src_ip` 字段！
4. 如果找不到对应的数据，请返回 "0 events found matching the query."。
5. 不要进行任何抱歉、解释等无关废话，你是一个没有感情的代码程序。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Execute Query: {search_query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"SIEM System Exception: Request Timeout. Underlying Error: {str(e)}"
