import os
import httpx
from openai import OpenAI

# Required environment variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_hpc_diag(query: str) -> str:
    """
    LLM-as-a-Mock implementation of the HPC Cloud Diagnosis API.
    Provides realistic data extraction for the VASP crash scenario.
    """
    if not query or len(query.strip()) < 5:
        return "Error: Invalid query. Please provide a detailed description of what you want to check, including the Ionic Step number."
    
    system_prompt = """你是一个名为 HPC-Cloud-VASP-Diag 的超算云端内存快照诊断系统 API。
你的任务是根据用户的查询返回 VASP 弛豫计算的受力数据。本任务的硬核背景设定如下，绝不能偏离：

1. 如果用户查询的离子步 (Ionic Step) 是 1 到 13 步，请告诉用户：该步收敛正常，所有原子的受力分量都在 -0.1 到 +0.1 eV/Angst 之间，没有发现异常。
2. 如果用户查询的离子步是 第 14 步（致命步），你必须报告：
   “检测到在第 14 个 Ionic Step 中发生了严重的能量发散。
   受力最大、导致系统崩溃的原子是第 42 号原子 (Atom Index: 42)。
   其受力分量为：Fx = 845.210, Fy = -991.330, Fz = 1502.440 (单位：eV/Angst)。”
   请注意：只提供受力分量，不要直接计算出总受力的绝对值，要求用户自己去计算。
3. 如果用户查询 14 步以上的步骤（如 15 步以后），告诉用户：“记录不存在，任务在第 14 步已经崩溃 (Segmentation fault)”。
4. 如果用户的提问中没有包含具体的“离子步/步数/Step”，请拒绝回答，并提示：“请在查询中明确指定您想要分析的具体 Ionic Step 序号，否则无法从庞大的内存堆栈中定位数据。”
5. 回答要以专业的终端诊断输出格式展示。"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Cloud connection failed. {str(e)}"
