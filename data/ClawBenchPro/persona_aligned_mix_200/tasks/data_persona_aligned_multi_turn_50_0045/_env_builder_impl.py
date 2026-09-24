import os
import argparse
import json

def build_turn_1():
    os.makedirs("metrics", exist_ok=True)
    os.makedirs("workloads", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    # Mock Prometheus JSON
    prometheus_data = {
        "nodes": {
            "k8s-node-1": {"allocatable_memory": 16384}, # 16 GiB
            "k8s-node-2": {"allocatable_memory": 16384},
            "k8s-node-3": {"allocatable_memory": 32768}, # 32 GiB
            "k8s-node-4": {"allocatable_memory": 65536}  # 64 GiB
        },
        "pod_metrics": [
            {"pod_name": "backend-api-7f8d", "namespace": "prod", "node": "k8s-node-1", "max_memory_usage": 14000}, # Spike!
            {"pod_name": "frontend-web-3a1b", "namespace": "prod", "node": "k8s-node-1", "max_memory_usage": 3000}, # 14000+3000 = 17000 > 16384 (OOM node-1)
            
            {"pod_name": "data-processor-5c5c", "namespace": "data", "node": "k8s-node-3", "max_memory_usage": 28000}, # Spike!
            {"pod_name": "fluentd-logging-1122", "namespace": "kube-system", "node": "k8s-node-3", "max_memory_usage": 6000}, # 28000+6000 = 34000 > 32768 (OOM node-3)
            
            {"pod_name": "cache-redis-99ab", "namespace": "cache", "node": "k8s-node-4", "max_memory_usage": 8000}, # Safe
            {"pod_name": "safe-app-001", "namespace": "default", "node": "k8s-node-2", "max_memory_usage": 4000}    # Safe
        ]
    }
    
    with open("metrics/prometheus_export.json", "w") as f:
        json.dump(prometheus_data, f, indent=2)

    # Mock YAML Workloads (Trap: cache-redis has 60Gi limit but usage is low, not the OOM cause. 
    # backend-api and data-processor are actual causes)
    workloads = {
        "backend-api.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-api
  namespace: prod
spec:
  template:
    spec:
      containers:
      - name: app
        resources:
          limits:
            memory: "15Gi"
""",
        "frontend.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-web
  namespace: prod
spec:
  template:
    spec:
      containers:
      - name: app
        resources:
          limits:
            memory: "4Gi"
""",
        "data-processor.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-processor
  namespace: data
spec:
  template:
    spec:
      containers:
      - name: processor
        resources:
          limits:
            memory: "30Gi"
""",
        "cache-redis.yaml": """apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: cache-redis
  namespace: cache
spec:
  template:
    spec:
      containers:
      - name: redis
        resources:
          limits:
            memory: "60Gi"
"""
    }

    for filename, content in workloads.items():
        with open(os.path.join("workloads", filename), "w") as f:
            f.write(content)

def build_turn_2():
    os.makedirs("network", exist_ok=True)
    
    # Mock Etcd Logs (split brain: node-3 and node-4 are partitioned)
    log_content = """[INFO] etcd server started
[WARN] node-4 missed 5 heartbeats, marking as unreachable.
[ERROR] peer connection lost to k8s-node-3, election timeout.
[INFO] node-1 healthy.
[INFO] node-2 healthy.
[ERROR] k8s-node-4 split-brain detected, segregating from cluster.
"""
    with open("network/etcd_health.log", "w") as f:
        f.write(log_content)

    # Mock Route JSON
    routes_data = {
        "k8s-node-1": {"status": "connected", "peers": ["k8s-node-2"]},
        "k8s-node-2": {"status": "connected", "peers": ["k8s-node-1"]},
        "k8s-node-3": {"status": "isolated", "peers": []},
        "k8s-node-4": {"status": "isolated", "peers": []}
    }
    with open("network/node_routes.json", "w") as f:
        json.dump(routes_data, f, indent=2)

def build_turn_3():
    os.makedirs("cluster", exist_ok=True)
    
    # Mock New Quotas (YAML)
    quotas_yaml = """apiVersion: v1
kind: ResourceQuota
metadata:
  name: prod-quota
  namespace: prod
spec:
  hard:
    limits.memory: "20Gi"
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: data-quota
  namespace: data
spec:
  hard:
    limits.memory: "32Gi"
"""
    with open("cluster/new_quotas.yaml", "w") as f:
        f.write(quotas_yaml)

    # Mock New Node Capacities
    # Traps: k8s-node-3 and k8s-node-4 have huge capacity, but they were partitioned in turn 2!
    # Valid new nodes are k8s-node-5 and k8s-node-6.
    nodes_data = {
        "k8s-node-3": {"status": "Ready", "allocatable_memory": 128000}, # TRAP: Partitioned in T2
        "k8s-node-4": {"status": "Ready", "allocatable_memory": 128000}, # TRAP: Partitioned in T2
        "k8s-node-5": {"status": "Ready", "allocatable_memory": 18000},  # Can fit backend-api (15Gi limit)
        "k8s-node-6": {"status": "Ready", "allocatable_memory": 36000}   # Can fit data-processor (30Gi limit)
    }
    with open("cluster/node_capacity.json", "w") as f:
        json.dump(nodes_data, f, indent=2)

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
