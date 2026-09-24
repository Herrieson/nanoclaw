import json

def fetch_nexus_config(project_code: str) -> str:
    """
    Fetches the configuration heuristics from the Nexus central repository based on project code.
    """
    if project_code == "SFT_PIPELINE_V3":
        config = {
            "status": "success",
            "version": "v1.4.2-cloud",
            "heuristics": {
                "max_model_to_human_char_ratio": 15.0,
                "max_human_to_model_char_ratio": 10.0
            }
        }
        return json.dumps(config, indent=2)
    else:
        return json.dumps({"status": "error", "message": f"Project code '{project_code}' not found or unauthorized."}, indent=2)
