import sys
import json

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python query_gpu_metrics_skill.py <instance_id>"}))
        sys.exit(1)
    
    instance_id = sys.argv[1].strip()
    
    # 模拟内部数据库的数据
    mock_db = {
        "i-0ffff111111111111": {"avg_gpu_util": "2.4%"},
        "i-0ffff222222222222": {"avg_gpu_util": "85.1%"},
        "i-0ffff333333333333": {"avg_gpu_util": "45.0%"}
    }
    
    if instance_id in mock_db:
        print(json.dumps(mock_db[instance_id]))
    else:
        print(json.dumps({"error": "Instance ID not found or no GPU attached."}))

if __name__ == "__main__":
    main()
