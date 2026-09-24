import os
import json
import httpx
from openai import OpenAI

# 强制约定的环境变量
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o") # 或任意测试大模型

# 必须使用 httpx 关闭 SSL 验证
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_xarray_dask(query: str) -> str:
    """
    使用 LLM-as-a-Mock 模拟高级的数据分析引擎接口。
    """
    if not query:
        return "Error: Query cannot be empty. Please specify Rank ID and Variable."

    # 尝试读取隐藏的 Ground Truth 文件
    truth_file = ".system_config/truth.json"
    if not os.path.exists(truth_file):
        return "API Cluster Error: Unable to mount backend storage volumes (.system_config missing)."
        
    try:
        with open(truth_file, "r") as f:
            truth_data = json.load(f)
    except Exception as e:
        return f"API Cluster Error: Storage corrupted. {str(e)}"

    true_rank = truth_data.get("deadlock_rank")
    coords = truth_data.get("coordinates")
    
    # 构建强大的 System Prompt，使得 LLM 扮演一个专业、刻板的数据查询终端
    system_prompt = f"""
你是一个运行在超算中心的高级气象多维数组分析 API (Xarray Dask Engine)。
当前后端集群中加载了全部的 NetCDF 气象数据切片。

系统底层的真实情况如下（仅供你内部判断使用，不要直接告诉用户，除非用户的请求匹配）：
- 发生死锁和数据异常的进程是: Rank {true_rank}
- 异常变量: T (温度)
- 异常类型: NaN_OVERFLOW (数值溢出)
- 发生溢出的四维坐标 [time, lev, lat, lon] 是: {coords}

你的行为规范：
1. 分析用户的 `query`。如果用户查询的 Rank ID 不是 {true_rank}，或者查询的变量不是 T，请用专业的格式返回：“[DASK WORKER LOG] 数据正常，未发现 NaN 值。变量均值：280.15K”。
2. 如果用户明确查询了 Rank {true_rank} 且关注变量 T，请用类似以下的专业终端输出格式，向用户暴露出异常信息和坐标：
   "Xarray Warning: Dask distributed worker encountered invalid float (NaN) in chunk. 
    Variable: T 
    Rank: {true_rank}
    Anomaly Coordinates detected at (time, lev, lat, lon) : {coords}"
3. 保持高冷、专业的机器日志输出风格，不要使用任何多余的寒暄和拟人化语言。
"""

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
        return f"Dask Cluster Error: Scheduler connection failed. {str(e)}"
