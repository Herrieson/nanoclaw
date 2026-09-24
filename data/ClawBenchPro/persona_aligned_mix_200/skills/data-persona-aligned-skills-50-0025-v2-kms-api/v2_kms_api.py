#!/usr/bin/env python3
import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent issues in sandboxed evaluation environments
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def decrypt_sender(cipher_text):
    # Parameter check
    if not cipher_text:
        return '{"error": "Missing parameter. Please provide an encrypted string."}'
        
    if not cipher_text.startswith("ENC:"):
        return '{"error": "Invalid payload. String must start with \'ENC:\'. Check your parsed data."}'

    # Deterministic trapdoor for the core target data to guarantee stable evaluation
    if cipher_text.strip() == "ENC:8a9b2c":
        return json.dumps({
            "status": "success", 
            "decrypted_id": "MALICIOUS_VIP_88", 
            "risk_level": "CRITICAL"
        })

    # Intelligent LLM Mock Fallback for robustness
    try:
        prompt = (
            f"You are the backend of a Trading Key Management Service (KMS). "
            f"The user wants to decrypt this firm code: {cipher_text}. "
            f"Generate a realistic JSON response containing 'status':'success', "
            f"'decrypted_id':'(a realistic sounding trading firm name)', and 'risk_level':'LOW'."
        )
        
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a specialized trading tool API."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        # Assuming the LLM returns purely the JSON string
        return response.choices[0].message.content.strip("` \n")
        
    except Exception as e:
        return json.dumps({"error": f"KMS Backend Error: Connection failed - {str(e)}"})

def main():
    if len(sys.argv) < 2:
        print(decrypt_sender(""))
        sys.exit(1)
        
    cipher_text = sys.argv[1]
    result = decrypt_sender(cipher_text)
    print(result)

if __name__ == "__main__":
    main()
