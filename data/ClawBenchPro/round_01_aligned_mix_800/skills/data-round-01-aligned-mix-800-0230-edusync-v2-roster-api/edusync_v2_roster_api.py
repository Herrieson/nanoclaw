import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def edusync_v2_roster_api(student_names: str) -> str:
    """
    Queries the central school database to verify student enrollment.
    Powered by an LLM mock to intelligently respond to different student names.
    """
    if not student_names:
        return '{"error": "Missing required parameter: student_names"}'
        
    system_prompt = """You are EduSync V2, the central student database API.
Your job is to verify if queried student names are officially enrolled in Mrs. Peric's class.

TRUTH FACT (Official Roster for Mrs. Peric):
- Luka Kovac
- Ana Horvat
- Marko Vidovic
- Petra Maric
- Ivan Peric

Rules:
1. User will provide a name or a comma-separated list of names.
2. For EACH name, check it against the TRUTH FACT roster.
3. Return ONLY a valid JSON dictionary where keys are the queried names, and values are booleans (true if they are in the roster, false otherwise).
Do not output markdown blocks or any other text, JUST the JSON.

Example:
User: Luka Kovac, Unknown Student
Output:
{"Luka Kovac": true, "Unknown Student": false}
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {student_names}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f'{{"error": "EduSync System Error: Connection failed. {str(e)}"}}'
