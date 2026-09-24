import os
import json
import random
from datetime import datetime, timedelta

def build_env():
    # 建立目录结构
    for d in ["billing", "policies", "metrics", "actions"]:
        os.makedirs(d, exist_ok=True)

    # 1. 深度嵌套且格式复杂的 Tag 映射策略 (模拟屎山配置)
    deep_policy = {
        "enterprise_cloud_governance": {
            "global_region": {
                "aws_gcp_combined": {
                    "v2_migration": {
                        "tag_mappings": {
                            "org_metadata": {
                                "version": "1.0.4",
                                "departments": {
                                    "AI-Research": {
                                        "cost_centers": [
                                            {"id": "CC-101", "obfuscated_tag": "0xAA11"},
                                            {"id": "CC-102", "obfuscated_tag": "0xAA12"}
                                        ]
                                    },
                                    "Data-Analytics": {
                                        "cost_centers": [
                                            {"id": "CC-201", "obfuscated_tag": "0xBB11"}
                                        ]
                                    },
                                    "Core-Prod": {
                                        "cost_centers": [
                                            {"id": "CC-999", "obfuscated_tag": "0xFF99"}
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    with open("policies/cost_center_tags.json", "w", encoding="utf-8") as f:
        json.dump(deep_policy, f, indent=4)

    # 2. 极其肮脏的账单导出数据
    # 列: 事务ID |~| 资源ID |~| 资源类型 |~| 状态 |~| 账单成本 |~| Hex标签
    billing_lines = [
        "TX_HEADER|~|RES_ID|~|TYPE|~|STATE|~|COST|~|TAG_HEX",
        "tx-001|~|vol-01aa|~|Block-Disk|~|Available|~|150.00|~|0xAA11",  # 目标: AI部门, 闲置磁盘
        "NULL_CORRUPT_LINE_0x000000",
        "tx-002|~|vol-02bb|~|Block-Disk|~|InUse|~|200.00|~|0xAA11",      # 干扰: AI部门, 正在使用
        "tx-003|~|vol-03cc|~|Block-Disk|~|Detached|~|50.00|~|0xBB11",   # 目标: Data部门, 闲置磁盘
        "ERROR: connection timeout on row 4",
        "tx-004|~|vol-04dd|~|Block-Disk|~|Available|~|300.00|~|0xFF99",  # 干扰: 核心生产部门, 闲置磁盘(权限外)
        "tx-005|~|i-gpu-01|~|Compute-GPU|~|Running|~|1000.00|~|0xAA12",  # 目标: AI部门, 低利用率GPU(需查日志)
        "tx-006|~|i-gpu-02|~|Compute-GPU|~|Running|~|1000.00|~|0xBB11",  # 干扰: Data部门, 高利用率GPU(需查日志)
        "tx-007|~|i-gpu-03|~|Compute-GPU|~|Running|~|1000.00|~|0xFF99",  # 干扰: 核心部门GPU(无权限)
        "tx-008|~|i-gpu-04|~|Compute-GPU|~|Running|~|1000.00|~|0xAA11",  # 目标: AI部门, 0利用率GPU
        "\n",
        "tx-009|~|snap-01|~|Snapshot|~|Available|~|10.00|~|0xAA11"      # 干扰: 快照不是磁盘或GPU
    ]
    with open("billing/raw_export_q3_v2.dat", "w", encoding="utf-8") as f:
        f.write("\n".join(billing_lines))

    # 3. 混乱无结构的 GPU syslog 指标打点日志
    log_lines = []
    base_time = datetime(2023, 10, 1, 0, 0, 0)
    for i in range(24):
        time_str = (base_time + timedelta(hours=i)).isoformat() + "Z"
        # 系统噪音
        log_lines.append(f"[{time_str}] systemd[1]: Started GPU Monitor Daemon.")
        log_lines.append(f"[{time_str}] kernel: nvrm: Xid (PCI:0000:00:00): 31, Ch 00000010")
        
        # i-gpu-01: 平均 util 非常低 (约 2-3%)
        log_lines.append(f"[{time_str}] gpu_metrics [INFO] res=i-gpu-01 util={random.randint(0, 4)}% mem=10%")
        
        # i-gpu-02: 平均 util 非常高 (约 90%)
        log_lines.append(f"[{time_str}] gpu_metrics [INFO] res=i-gpu-02 util={random.randint(85, 99)}% mem=90%")
        
        # i-gpu-03: 平均 util 低，但属于 Core-Prod，干扰项
        log_lines.append(f"[{time_str}] gpu_metrics [INFO] res=i-gpu-03 util={random.randint(0, 5)}% mem=5%")
        
        # i-gpu-04: 死机/完全没流量的闲置机器
        log_lines.append(f"[{time_str}] gpu_metrics [INFO] res=i-gpu-04 util=0% mem=0%")
        
        # 其他噪音日志
        if i % 3 == 0:
            log_lines.append(f"[{time_str}] kernel: [ 1234.5678] usb 1-1: USB disconnect, device number {i}")

    # 随机打乱日志行，模拟异步聚合导致的日志乱序
    random.shuffle(log_lines)
    
    with open("metrics/gpu_syslog.log", "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

if __name__ == "__main__":
    build_env()
