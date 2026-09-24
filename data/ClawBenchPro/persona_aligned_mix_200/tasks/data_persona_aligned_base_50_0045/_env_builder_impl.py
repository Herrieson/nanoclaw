import os
import json
import random
import uuid

def build_env():
    # 创建所需的工作目录，当前执行路径已被系统设定为 assets/data_persona_aligned_base_50_0045/
    os.makedirs('diagnostics', exist_ok=True)
    os.makedirs('manifests', exist_ok=True)
    os.makedirs('incident_report', exist_ok=True)

    # ==========================================
    # 1. 生成带有乱码、十六进制碎片的 Kubelet 日志
    # ==========================================
    target_container_id = "f9b2c3a1d4e5f6g7h8i9j0"
    
    log_lines = []
    # 注入一些正常日志
    for i in range(120):
        minute = random.randint(10, 39)
        second = random.randint(10, 59)
        log_lines.append(f"2024-05-15T03:{minute}:{second}Z infra-core-04 kubelet: [INFO] SyncLoop (PLEG): pod update for calico-node-{i}".encode())
        # 随机混入二进制乱码 (模拟 syslog 损坏)
        if random.random() < 0.15:
            log_lines.append(os.urandom(12))

    # 注入核心 OOM 日志行，隐藏在大量噪声中
    oom_msg = (
        f"2024-05-15T03:41:22Z infra-core-04 kernel: [38192.102] Memory cgroup out of memory: "
        f"Killed process 8812 (java) total-vm:16384000kB, anon-rss:8192000kB, file-rss:0kB, shmem-rss:0kB. "
        f"oom_kill_target: cgroup=/kubepods/burstable/pod-uid-xxxx/container-{target_container_id}"
    )
    log_lines.append(oom_msg.encode())

    # 注入驱逐风暴日志
    for i in range(80):
        minute = random.randint(42, 59)
        log_lines.append(f"2024-05-15T03:{minute}:11Z infra-core-04 kubelet: [WARN] Evicting pod due to NodeHasNoMemory".encode())

    with open('diagnostics/kubelet_syslog.log', 'wb') as f:
        # 文件头写入破坏性二进制数据
        f.write(b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a") 
        f.write(b"==== KUBELET CRASH DUMP ====\n")
        for line in log_lines:
            f.write(line + b"\n")

    # ==========================================
    # 2. 生成非标准格式的 Prometheus 导出数据 (首尾有乱码的深层 JSON)
    # ==========================================
    prom_data = {
        "status": "success",
        "data": {
            "resultType": "vector",
            "result": []
        }
    }
    
    # 混淆项容器
    for i in range(35):
        prom_data["data"]["result"].append({
            "metric": {
                "__name__": "kube_pod_container_info",
                "container_id": f"docker://{uuid.uuid4().hex[:16]}",
                "namespace": random.choice(["kube-system", "monitoring", "default"]),
                "pod": f"random-service-pod-{i}"
            },
            "value": [1715093822, "1"]
        })
        
    # 目标容器
    target_pod_name = "core-payment-gateway-deployment-78dbb9c4"
    target_namespace = "finance-production"
    prom_data["data"]["result"].append({
        "metric": {
            "__name__": "kube_pod_container_info",
            "container_id": f"containerd://{target_container_id}",
            "namespace": target_namespace,
            "pod": target_pod_name
        },
        "value": [1715093822, "1"]
    })

    # 将 JSON 写入并包裹在脏数据中，使标准 json.load 直接崩溃
    with open('diagnostics/prom_metrics_dump.json', 'w', encoding='utf-8') as f:
        f.write("HTTP/1.1 502 Bad Gateway\n")
        f.write("X-Prometheus-Err: \x00\xFF_memory_corruption\n")
        f.write("----BEGIN_JSON_PAYLOAD----\n")
        json.dump(prom_data, f, indent=2)
        f.write("\n----END_JSON_PAYLOAD----\n")
        f.write("\x04\x00\x00\x00EOF")

    # ==========================================
    # 3. 生成大量 YAML 配置（包含语法错误的干扰项）
    # ==========================================
    # 干扰 YAML
    for i in range(60):
        is_broken = (i % 8 == 0)
        ns = random.choice(["logistics-prod", "crm-prod", "finance-production", "default"])
        yaml_content = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: noise-service-{i}
  namespace: {ns}
  annotations:
    owner_team: "squad-{i}-{'broken' if is_broken else 'ok'}"
spec:
  replicas: 2
  template:
    metadata:
      labels:
        app: noise-{i}
    spec:
      containers:
      - name: app
        image: nginx:latest
"""
        if is_broken:
            yaml_content += "      bad_indent: \nvalue-missing-quotes"
            
        with open(f'manifests/deploy_noise_{i}.yaml', 'w', encoding='utf-8') as f:
            f.write(yaml_content)

    # 目标 YAML (注意：Deployment 名字是 Pod 名字的前缀)
    target_yaml = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: core-payment-gateway-deployment
  namespace: {target_namespace}
  annotations:
    prometheus.io/scrape: "true"
    owner_team: "billing-core-team"
    incident_level: "P0"
spec:
  replicas: 10
  template:
    metadata:
      labels:
        app: core-payment
    spec:
      containers:
      - name: jvm-processor
        image: java-app:1.8
        resources:
          limits:
            memory: "16Gi"
            cpu: "8"
"""
    with open('manifests/deploy_payment_gateway.yaml', 'w', encoding='utf-8') as f:
        f.write(target_yaml)

if __name__ == "__main__":
    build_env()
