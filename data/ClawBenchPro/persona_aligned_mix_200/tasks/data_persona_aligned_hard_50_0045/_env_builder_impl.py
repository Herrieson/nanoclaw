import os
import json
import random
import uuid
import string

def build_env():
    # 建立核心目录，当前执行路径已被设定为 assets/data_persona_aligned_hard_50_0045/
    os.makedirs('incident_report', exist_ok=True)
    
    # 动态生成目标数据，防止静态匹配作弊
    target_container_id = f"cont_{uuid.uuid4().hex}"
    target_deploy_name = "payment-gateway-engine-v3"
    target_pod_name = f"{target_deploy_name}-7b9d4c8f5-x2w9q"
    target_namespace = "finance-critical-prod"
    target_team = "core-billing-strike-team"

    # ==========================================
    # 1. 生成极度碎片化且包含噪声的 Syslogs
    # ==========================================
    nodes = [f"infra-core-{str(i).zfill(2)}" for i in range(1, 15)]
    for node in nodes:
        node_dir = os.path.join('diagnostics', 'syslogs', node)
        os.makedirs(node_dir, exist_ok=True)
        
        # 每个节点切分为 15 个日志碎片
        for chunk in range(15):
            log_path = os.path.join(node_dir, f"kubelet.log.chunk-{chunk}")
            with open(log_path, 'wb') as f:
                # 注入大量垃圾二进制模拟文件损坏
                f.write(os.urandom(random.randint(128, 512)))
                f.write(b"\n")
                
                # 注入正常但无用的日志
                for _ in range(50):
                    f.write(f"2024-05-15T03:41:{random.randint(10,59)}Z {node} kubelet: [INFO] PLEG sync pod-id-{uuid.uuid4().hex[:8]}\n".encode('utf-8'))
                
                # 在特定节点的特定碎片隐蔽注入真理
                if node == "infra-core-04" and chunk == 7:
                    oom_line = (
                        f"2024-05-15T03:41:22Z {node} kernel: [38192.102] Memory cgroup out of memory: "
                        f"Killed process 8812 (java) total-vm:16384000kB. "
                        f"oom_kill_target: cgroup=/kubepods/burstable/pod-uid-x/container-{target_container_id}\n"
                    )
                    f.write(oom_line.encode('utf-8'))
                
                # 注入干扰性假 OOM
                if random.random() < 0.2:
                    fake_id = f"cont_{uuid.uuid4().hex}"
                    fake_oom = f"kernel: Memory cgroup warning: process 1234 oom_kill_target: container-{fake_id}\n"
                    f.write(fake_oom.encode('utf-8'))

                f.write(os.urandom(random.randint(64, 256)))

    # ==========================================
    # 2. 生成包含畸形前缀的 Prometheus 分片数据
    # ==========================================
    prom_dir = os.path.join('diagnostics', 'prom_metrics')
    os.makedirs(prom_dir, exist_ok=True)
    
    for i in range(40):
        # 构造带有大量干扰项的指标数据
        prom_data = {"status": "success", "data": {"resultType": "vector", "result": []}}
        for _ in range(15):
            prom_data["data"]["result"].append({
                "metric": {
                    "__name__": "kube_pod_container_info",
                    "container_id": f"docker://cont_{uuid.uuid4().hex}",
                    "namespace": random.choice(["default", "monitoring", "kube-system", target_namespace]),
                    "pod": f"random-svc-{uuid.uuid4().hex[:6]}-pod"
                },
                "value": [1715093822, "1"]
            })
            
        # 在第 23 个分片植入目标
        if i == 23:
            prom_data["data"]["result"].append({
                "metric": {
                    "__name__": "kube_pod_container_info",
                    "container_id": f"containerd://{target_container_id}",
                    "namespace": target_namespace,
                    "pod": target_pod_name
                },
                "value": [1715093822, "1"]
            })
            
        # 故意制造非标 JSON 包装
        with open(os.path.join(prom_dir, f"scrape_shard_{i}.json"), 'w', encoding='utf-8') as f:
            f.write("HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
            f.write("<<<STREAM_START>>>\n")
            json.dump(prom_data, f)
            f.write("\n<<<STREAM_END>>>\n\x00\xff")

    # ==========================================
    # 3. 生成巨型、混乱且带有语法错误的 YAML 森林
    # ==========================================
    namespaces = ["default", "finance-critical-prod", "crm-backend", "logistics-db"]
    for i in range(300):
        # 创建深层随机目录结构
        depth = random.randint(1, 3)
        sub_dir = "/".join(["".join(random.choices(string.ascii_lowercase, k=5)) for _ in range(depth)])
        manifest_dir = os.path.join('manifests', sub_dir)
        os.makedirs(manifest_dir, exist_ok=True)
        
        is_broken = (random.random() < 0.25)
        ns = random.choice(namespaces)
        name = f"service-{uuid.uuid4().hex[:8]}"
        
        yaml_content = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
  namespace: {ns}
  annotations:
    owner_team: "team-{uuid.uuid4().hex[:4]}"
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
      - name: main
        image: nginx:1.14
"""
        # 制造 YAML 语法错误 (破坏缩进或未闭合引号)
        if is_broken:
            yaml_content += f"      broken_field: 'unclosed quote\n        bad_indent: yes\n"
            
        with open(os.path.join(manifest_dir, f"deploy_{i}.yaml"), 'w', encoding='utf-8') as f:
            f.write(yaml_content)

    # 埋入真正的目标 YAML (深藏在某个合法路径)
    target_manifest_dir = os.path.join('manifests', 'prod', 'finance', 'gateway')
    os.makedirs(target_manifest_dir, exist_ok=True)
    target_yaml = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {target_deploy_name}
  namespace: {target_namespace}
  labels:
    tier: critical
  annotations:
    prometheus.io/scrape: "true"
    owner_team: "{target_team}"
spec:
  replicas: 5
  template:
    metadata:
      labels:
        app: payment-gateway
    spec:
      containers:
      - name: jvm-processor
        image: openjdk:11-jre
        resources:
          limits:
            memory: "32Gi"
"""
    with open(os.path.join(target_manifest_dir, 'deployment.yaml'), 'w', encoding='utf-8') as f:
        f.write(target_yaml)

if __name__ == "__main__":
    build_env()
