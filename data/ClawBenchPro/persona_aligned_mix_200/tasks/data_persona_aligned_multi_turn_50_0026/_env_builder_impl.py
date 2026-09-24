import os
import argparse
import json
import yaml
import csv

def build_turn_1():
    os.makedirs("configs", exist_ok=True)
    os.makedirs("traces_batch_1", exist_ok=True)
    os.makedirs("workspace", exist_ok=True)

    # 生成配置文件
    whitelist = {
        "services": {
            "order-service": {"tier": 1},
            "inventory-service": {"tier": 1},
            "payment-gateway": {"tier": 1},
            "user-profile": {"tier": 1},
            "recommendation-service": {"tier": 2},
            "notification-service": {"tier": 2},
            "log-collector": {"tier": 3}
        }
    }
    with open("configs/service_whitelist.yaml", "w") as f:
        yaml.dump(whitelist, f)

    # 生成 Trace 数据 (Batch 1)
    # 干扰项 1: Root < 850 (800) -> 忽略
    t101 = {
        "traceId": "trace-101-b1",
        "spans": [
            {"spanId": "s1", "parentId": None, "serviceName": "api-gateway", "duration_ms": 800, "tags": {"node": "gateway-1"}},
            {"spanId": "s2", "parentId": "s1", "serviceName": "order-service", "duration_ms": 780, "tags": {"node": "node-A1", "error": False}}
        ]
    }
    
    # 干扰项 2: Root > 850 (900), 但最慢子 span 是 tier 2 -> 忽略
    t102 = {
        "traceId": "trace-102-b1",
        "spans": [
            {"spanId": "s1", "parentId": None, "serviceName": "api-gateway", "duration_ms": 900, "tags": {"node": "gateway-2"}},
            {"spanId": "s2", "parentId": "s1", "serviceName": "recommendation-service", "duration_ms": 880, "tags": {"node": "node-R1", "error": False}},
            {"spanId": "s3", "parentId": "s1", "serviceName": "order-service", "duration_ms": 100, "tags": {"node": "node-A1", "error": False}}
        ]
    }

    # 命中项 1: Root > 850 (880), 最慢子 span 是 tier 1 (order-service, 700ms) -> 抓出
    t103 = {
        "traceId": "trace-103-b1",
        "spans": [
            {"spanId": "s1", "parentId": None, "serviceName": "api-gateway", "duration_ms": 880, "tags": {"node": "gateway-1"}},
            {"spanId": "s2", "parentId": "s1", "serviceName": "order-service", "duration_ms": 700, "tags": {"node": "node-A1", "error": False}},
            {"spanId": "s3", "parentId": "s2", "serviceName": "inventory-service", "duration_ms": 150, "tags": {"node": "node-I1", "error": False}}
        ]
    }

    # 命中项 2: Root > 850 (920), 最慢子 span 是 tier 1 (user-profile, 800ms) -> 抓出
    t104 = {
        "traceId": "trace-104-b1",
        "spans": [
            {"spanId": "s1", "parentId": None, "serviceName": "api-gateway", "duration_ms": 920, "tags": {"node": "gateway-3"}},
            {"spanId": "s2", "parentId": "s1", "serviceName": "user-profile", "duration_ms": 800, "tags": {"node": "node-U1", "error": True, "errorType": "DBTimeout"}}
        ]
    }

    traces = [t101, t102, t103, t104]
    for idx, t in enumerate(traces):
        with open(f"traces_batch_1/trace_segment_{idx}.json", "w") as f:
            json.dump(t, f, indent=2)

def build_turn_2():
    os.makedirs("traces_batch_2", exist_ok=True)
    
    # 必须假设工作区包含了 turn_1 的产物。我们只负责生成增量数据。
    
    # 干扰项 (基于新规则): Root > 850, tier 1 是 payment-gateway, errorType: RateLimitRetry -> 豁免
    t201 = {
        "traceId": "trace-201-b2",
        "spans": [
            {"spanId": "s1", "parentId": None, "serviceName": "api-gateway", "duration_ms": 950, "tags": {"node": "gateway-1"}},
            {"spanId": "s2", "parentId": "s1", "serviceName": "payment-gateway", "duration_ms": 920, "tags": {"node": "node-P1", "error": True, "errorType": "RateLimitRetry"}}
        ]
    }

    # 命中项 3 (不被豁免的 payment): Root > 850, tier 1 是 payment-gateway, errorType: ConnectionRefused -> 抓出
    t202 = {
        "traceId": "trace-202-b2",
        "spans": [
            {"spanId": "s1", "parentId": None, "serviceName": "api-gateway", "duration_ms": 910, "tags": {"node": "gateway-2"}},
            {"spanId": "s2", "parentId": "s1", "serviceName": "payment-gateway", "duration_ms": 890, "tags": {"node": "node-P2", "error": True, "errorType": "ConnectionRefused"}}
        ]
    }

    # 命中项 4: 普通的 tier 1 超时 -> 抓出
    t203 = {
        "traceId": "trace-203-b2",
        "spans": [
            {"spanId": "s1", "parentId": None, "serviceName": "api-gateway", "duration_ms": 870, "tags": {"node": "gateway-1"}},
            {"spanId": "s2", "parentId": "s1", "serviceName": "inventory-service", "duration_ms": 850, "tags": {"node": "node-I2", "error": False}}
        ]
    }
    
    # 干扰项 (老规则): Root = 840 (不到 850)
    t204 = {
        "traceId": "trace-204-b2",
        "spans": [
            {"spanId": "s1", "parentId": None, "serviceName": "api-gateway", "duration_ms": 840, "tags": {"node": "gateway-3"}},
            {"spanId": "s2", "parentId": "s1", "serviceName": "order-service", "duration_ms": 820, "tags": {"node": "node-A2", "error": False}}
        ]
    }

    traces = [t201, t202, t203, t204]
    for idx, t in enumerate(traces):
        with open(f"traces_batch_2/trace_segment_b2_{idx}.json", "w") as f:
            json.dump(t, f, indent=2)

def build_turn_3():
    os.makedirs("sre_data", exist_ok=True)
    
    # 包含了所有可能节点的状态数据
    # 命中项1 (t103): node-A1 -> HighLoad (SRE背锅)
    # 命中项2 (t104): node-U1 -> Normal (应用背锅)
    # 命中项3 (t202): node-P2 -> NetworkJitter (SRE背锅)
    # 命中项4 (t203): node-I2 -> Normal (应用背锅)
    
    # 干扰项：node-P1(被豁免的) -> HighLoad
    
    csv_data = [
        ["node_id", "status", "region", "cpu_util"],
        ["node-A1", "HighLoad", "us-east", "98%"],
        ["node-U1", "Normal", "us-east", "45%"],
        ["node-P1", "HighLoad", "us-west", "99%"],
        ["node-P2", "NetworkJitter", "us-west", "30%"],
        ["node-I2", "Normal", "eu-central", "50%"],
        ["node-R1", "Normal", "us-east", "60%"],
        ["node-A2", "Normal", "us-east", "40%"]
    ]
    
    with open("sre_data/node_status.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turn", type=int, required=True)
    args = parser.parse_args()
    
    if args.turn == 1:
        build_turn_1()
    elif args.turn == 2:
        build_turn_2()
    elif args.turn == 3:
        build_turn_3()
