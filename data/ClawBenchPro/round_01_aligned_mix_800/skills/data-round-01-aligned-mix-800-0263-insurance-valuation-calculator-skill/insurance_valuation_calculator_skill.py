import sys
import json

def main():
    try:
        line = sys.stdin.read()
        if not line:
            return
        params = json.loads(line)
        
        base_price = float(params.get("base_price", 0))
        # 模拟复杂的保险算法：Base * 1.15 + 50 (固定服务费)
        # 注意：verify_rules.py 会校验这个结果
        certified_value = (base_price * 1.15) + 50
        
        result = {
            "certified_value": certified_value,
            "formula_used": "Market_Value * 1.15 + 50 (Standard Premium Adjustment)"
        }
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": "Invalid input. Please provide a numeric base_price."}))

if __name__ == "__main__":
    main()
