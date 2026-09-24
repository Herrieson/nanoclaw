import os
import httpx
from openai import OpenAI

# Standard Mock Env Vars
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# Disable SSL verification for isolated eval environments
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_ticket(ticket_id: str):
    """
    Uses LLM-as-a-Mock to simulate querying the modern Cloud Ticket API.
    Injects specific ground-truth rules for objective evaluation.
    """
    if not ticket_id:
        return "GraphQL Error: ticket_id cannot be null."
        
    ticket_id = ticket_id.strip().upper()
    
    system_prompt = f"""
    你是一个名为 'Cloud Ticket GraphQL API' 的企业内部客服工单系统的虚拟后端。
    请根据用户提供的 Ticket ID ({ticket_id})，返回该工单的详细客户投诉内容(customer_complaint)。
    
    【核心事实要求 - 必须绝对服从】：
    - 如果 ticket_id 是 "T-5001"，你返回的内容中**必须**包含原话："The artisan carving was completely fake plastic. Furious. No one helped me."
    - 如果 ticket_id 是 "T-5003"，你返回的内容中**必须**包含原话："Received a broken ceramic bowl. Customer service hung up on me."
    - 如果 ticket_id 是 "T-5002"，请简述一件衣服缩水的事情："T-shirt shrank after one wash."
    - 对于任何其他 ticket_id，请根据零售业"Global Heritage"或"Tech Gadgets"的语境，合理编造一段简短（1-2句话）的英文客户投诉。
    
    只输出投诉内容的纯文本，不要输出JSON或解释。
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Querying ticket: {ticket_id}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback to hardcoded string to prevent total eval failure if API crashes
        if ticket_id == "T-5001":
            return "The artisan carving was completely fake plastic. Furious. No one helped me."
        elif ticket_id == "T-5003":
            return "Received a broken ceramic bowl. Customer service hung up on me."
        return f"System Error: API Gateway timeout. {str(e)}"
