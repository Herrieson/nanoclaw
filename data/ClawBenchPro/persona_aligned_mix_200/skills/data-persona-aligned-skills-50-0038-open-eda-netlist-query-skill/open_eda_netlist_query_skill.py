import os
import sys
import json
import httpx
from openai import OpenAI

# MOCK API 配置
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def execute(query_string):
    if not query_string:
        return "Error: query_string cannot be empty."

    # LLM-as-a-Mock：提供兜底和智能数据返回
    system_prompt = """
    You are an Open-Source EDA Netlist Query Tool. 
    Your job is to parse the user's query about an encrypted .enc netlist mapping database, and return the correct module instance path.
    
    Context Truth for this specific SoC Simulation task:
    - If the user asks about the signal "axi_awaddr" or "axi_awvalid", the absolute correct instance path that drives it is: "sys_top.bus_matrix.u_axi_interconnect_m0"
    - If the user asks about any other signal, you can return a random plausible module path (e.g. sys_top.domain_cpu.subsys_x).
    
    Respond cleanly with just the query results and the exact module instance path. Do not break character.
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Query: {query_string}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: LLM Mock Connection failed. {str(e)}"
