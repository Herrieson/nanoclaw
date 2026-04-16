import os
import json

def verify():
    # 优先检查评测容器内的挂载路径，如果没有则回退至本地 assets 目录用于测试
    base_dir = "pump_system"
    if not os.path.exists(base_dir):
        base_dir = "pump_system"
        
    state = {
        "identified_correct_pump": False,
        "average_calculated_correctly": False,
        "config_updated_correctly": False
    }
    
    # 验证第一步：计算故障泵(Pump B)的平均压力
    avg_file = os.path.join(base_dir, "bad_pump_avg.txt")
    if os.path.exists(avg_file):
        with open(avg_file, 'r') as f:
            val = f.read().strip()
            # Average of B: (100 + 85 + 75 + 60 + 40) / 5 = 72
            if "72" in val:
                state["identified_correct_pump"] = True
                state["average_calculated_correctly"] = True
                
    # 验证第二步：正确修改 JSON 配置状态
    config_file = os.path.join(base_dir, "system_config.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                data = json.load(f)
                pump_b = data.get("pumps", {}).get("B", {})
                
                status = pump_b.get("status", "").lower()
                backup_status = pump_b.get("backup_status", "").lower()
                
                # 由于 persona 提示比较模糊，验证规则宽容处理常见的关闭/启动术语
                if status in ["offline", "disabled", "down", "inactive"]:
                    if backup_status in ["online", "active", "up", "running"]:
                        state["config_updated_correctly"] = True
        except Exception:
            pass
            
    # 输出结构化裁判文件
    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
