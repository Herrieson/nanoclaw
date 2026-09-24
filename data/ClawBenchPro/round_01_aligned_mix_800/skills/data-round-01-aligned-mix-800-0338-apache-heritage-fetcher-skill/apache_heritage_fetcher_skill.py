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

def fetch_heritage_text(sync_id: str) -> str:
    """
    Fetches the original digitized text from the Heritage Cloud based on the given SYNC_ID.
    """
    if not sync_id:
        return "Error: Missing sync_id parameter."

    # Clean the input to handle cases where agent passes "SYNC_ID: APACHE-..."
    clean_id = sync_id.replace("SYNC_ID:", "").strip()

    system_prompt = """You are the backend API for the Apache Heritage Digital Archive. 
You strictly return the following exact texts based on the ID provided, to ensure historical accuracy.
If ID is 'APACHE-A12', return EXACTLY: 'The old ones used to say that peace is found in the stillness of the desert. Our Apache ancestors walked these lands with respect.'
If ID is 'APACHE-B34', return EXACTLY: 'Auntie's frybread recipe: 2 cups flour, 1 tablespoon baking powder, 1/2 teaspoon salt, 1 cup warm water. Fry in oil until golden. A simple tradition.'
If ID is 'APACHE-C56', return EXACTLY: 'My grandfather told me the story of the bear. He said it teaches us equality among all living creatures. We must preserve our heritage.'
If ID is 'APACHE-D78', return EXACTLY: 'Sitting by the window today. I prefer the solitude. Thinking about the traditional ceremonies back in Arizona.'
If the ID does not match any of the above, creatively simulate a realistic 404 API Not Found error message."""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Requesting document for ID: {clean_id}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: Connection to Heritage Cloud failed. {str(e)}"
