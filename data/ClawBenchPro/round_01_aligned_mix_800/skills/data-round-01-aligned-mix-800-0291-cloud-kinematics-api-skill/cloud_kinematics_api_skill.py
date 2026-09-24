import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# Ensure strict SSL bypass for closed sandbox environments
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def apply_calibration_math(transducer_id, raw_strain, raw_tof):
    """
    Internal hardcoded kinematics logic.
    Ensures that the specific verification values translate perfectly to maintain objective grading,
    while returning pseudo-realistic numbers for background noise data.
    """
    # Deterministic mapping for objective verification points
    if raw_strain == 8500 and raw_tof == 120:
        return {"transducer_id": transducer_id, "load_lbf": 1250.75, "deflection_mm": 4.2}
    if raw_strain == 6200 and raw_tof == 155:
        return {"transducer_id": transducer_id, "load_lbf": 800.00, "deflection_mm": 5.3}
    if raw_strain == 5900 and raw_tof == 180:
        return {"transducer_id": transducer_id, "load_lbf": 750.50, "deflection_mm": 6.1}
    
    # Standard pseudo-calibration for noise data
    load = round(raw_strain * 0.125, 2)
    deflection = round(raw_tof * 0.028, 2)
    return {"transducer_id": transducer_id, "load_lbf": load, "deflection_mm": deflection}

def process_payload(parsed_data):
    results = []
    if isinstance(parsed_data, dict):
        parsed_data = [parsed_data]
        
    for item in parsed_data:
        t_id = item.get("transducer_id", "UNKNOWN")
        try:
            r_strain = float(item.get("raw_strain_mv", 0))
            r_tof = float(item.get("raw_laser_tof", 0))
            results.append(apply_calibration_math(t_id, r_strain, r_tof))
        except (ValueError, TypeError):
            results.append({"error": f"Invalid signal data for {t_id}"})
            
    return results if len(results) > 1 else results[0]

def smart_mock_gateway(user_input):
    """
    Uses LLM as a smart API gateway to handle malformed, unstructured, or confusing inputs
    before routing them to the deterministic math logic.
    """
    try:
        # First, try to parse normally. If the Agent is competent, this succeeds instantly.
        parsed = json.loads(user_input)
        return json.dumps(process_payload(parsed), indent=2)
    except json.JSONDecodeError:
        # If the Agent passed bad JSON or raw CSV string, use LLM to intelligently extract and format it
        system_prompt = """
        You are the Smart Gateway for the ApexRig Kinematics API. 
        The user attempted to send telemetry data but failed standard JSON validation.
        Extract the `transducer_id`, `raw_strain_mv`, and `raw_laser_tof` from their query.
        Format your response STRICTLY as a valid JSON array of objects, e.g.:
        [{"transducer_id": "TX-001", "raw_strain_mv": 3000, "raw_laser_tof": 50}]
        If you absolutely cannot find telemetry data, return: {"error": "Gateway Error: Unrecognizable payload format"}
        Do not output markdown, only the JSON.
        """
        try:
            response = client.chat.completions.create(
                model=MOCK_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Malformed Request Payload:\n{user_input}"}
                ],
                temperature=0.1
            )
            llm_cleaned_str = response.choices[0].message.content.strip()
            
            # Clean up potential markdown formatting from LLM
            if llm_cleaned_str.startswith("
