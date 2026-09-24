import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_mission_icd(query: str) -> str:
    if not query:
        return "Error: Missing required parameter 'query'."
    
    system_prompt = """You are the Nova-7 Mission Control Interface Control Document (ICD) database API. 
You provide exact technical specifications for satellite telemetry protocols based on user queries.

CRITICAL RULES FOR RESPONDING:
If the user asks about "Star Tracker", "Attitude", or "Quaternions" for Nova-7, you MUST return the following EXACT technical details:
- Frame Structure: [SYNC_WORD] [PAYLOAD_LEN] [SUBSYS_ID] [PAYLOAD] [CHECKSUM]
- Sync Word: 0xA5 0x5A (2 bytes)
- Payload Length (PAYLOAD_LEN): 0x10 (1 byte, indicates 16 bytes of payload)
- Subsystem ID (SUBSYS_ID): 0x07 (1 byte, signifies Star Tracker Attitude Data)
- Payload Format: Four 32-bit IEEE 754 floating-point numbers.
- Endianness: Big-Endian format.
- Data Order: q_w, q_x, q_y, q_z.
- Checksum: 1 Byte XOR (Do not enforce due to BER).

If the user asks about other subsystems like EPS or TCS, invent plausible but distinct IDs (e.g., EPS is 0x02, TCS is 0x04) and lengths. Be concise and technical."""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Database Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: API connectivity failure. {str(e)}"
