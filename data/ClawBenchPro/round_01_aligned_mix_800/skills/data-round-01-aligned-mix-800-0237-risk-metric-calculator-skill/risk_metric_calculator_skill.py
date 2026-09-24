import sys
import json

def calculate_risk(score, transcript):
    # 基础风险由分数决定 (反比)
    base_risk = (100 - score) / 100.0
    
    # 如果转录中包含关键词，风险激增
    keywords = ["Child Safety", "Housing Instability", "Severe neglect"]
    multiplier = 1.0
    if transcript:
        for kw in keywords:
            if kw.lower() in transcript.lower():
                multiplier += 0.3
    
    return min(1.0, base_risk * multiplier)

if __name__ == "__main__":
    try:
        data = json.loads(sys.argv[1])
        score = data.get("score", 50)
        transcript = data.get("transcript", "")
        print(json.dumps({"risk_index": calculate_risk(score, transcript)}))
    except:
        print(json.dumps({"error": "Invalid input"}))
