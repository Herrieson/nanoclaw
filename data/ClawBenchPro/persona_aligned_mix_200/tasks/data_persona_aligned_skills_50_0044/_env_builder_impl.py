import os
import json

def build_env():
    # 建立目录结构
    for d in ["billing", "policies", "actions"]:
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

    # 2. 极其肮脏的账单导出数据 - Tag已经被哈希脱敏
    # 列: 事务ID |~| 资源ID |~| 资源类型 |~| 状态 |~| 账单成本 |~| Hash标签
    billing_lines = [
        "TX_HEADER|~|RES_ID|~|TYPE|~|STATE|~|COST|~|HASH_TAG",
        "tx-001|~|vol-01aa|~|Block-Disk|~|Available|~|150.00|~|FIN_HASH_A1",  # 目标: AI部门(0xAA11), 闲置磁盘
        "NULL_CORRUPT_LINE_0x000000",
        "tx-002|~|vol-02bb|~|Block-Disk|~|InUse|~|200.00|~|FIN_HASH_A1",      # 干扰: AI部门, 正在使用
        "tx-003|~|vol-03cc|~|Block-Disk|~|Detached|~|50.00|~|FIN_HASH_B1",   # 目标: Data部门(0xBB11), 闲置磁盘
        "ERROR: connection timeout on row 4",
        "tx-004|~|vol-04dd|~|Block-Disk|~|Available|~|300.00|~|FIN_HASH_F9",  # 干扰: 核心生产部门(0xFF99), 闲置磁盘(权限外)
        "tx-005|~|i-gpu-01|~|Compute-GPU|~|Running|~|1000.00|~|FIN_HASH_A2",  # 目标: AI部门(0xAA12), 低利用率GPU(需查API)
        "tx-006|~|i-gpu-02|~|Compute-GPU|~|Running|~|1000.00|~|FIN_HASH_B1",  # 干扰: Data部门(0xBB11), 高利用率GPU(需查API)
        "tx-007|~|i-gpu-03|~|Compute-GPU|~|Running|~|1000.00|~|FIN_HASH_F9",  # 干扰: 核心部门GPU(无权限)
        "tx-008|~|i-gpu-04|~|Compute-GPU|~|Running|~|1000.00|~|FIN_HASH_A1",  # 目标: AI部门(0xAA11), 0利用率GPU
        "\n",
        "tx-009|~|snap-01|~|Snapshot|~|Available|~|10.00|~|FIN_HASH_A1"      # 干扰: 快照不是磁盘或GPU
    ]
    with open("billing/raw_export_q3_v2.dat", "w", encoding="utf-8") as f:
        f.write("\n".join(billing_lines))

if __name__ == "__main__":
    build_env()
