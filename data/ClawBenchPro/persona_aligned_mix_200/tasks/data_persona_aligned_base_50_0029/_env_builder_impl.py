import os
import base64

def build_env():
    # 确保在当前工作目录（已被框架置为 assets/data_persona_aligned_base_50_0029/）下直接创建文件夹
    os.makedirs("cur_dumps", exist_ok=True)
    os.makedirs("metrics", exist_ok=True)
    os.makedirs("action_items", exist_ok=True)

    # 1. 构造极度混乱的 CUR 计费流日志
    # 包含正常的Base64记录、单引号伪JSON、夹杂在乱码中的资源信息
    cur_log_content = """STREAM_START|0x7A9B|REGION:us-east-1|VER:3.1.4
WARN: Data pipeline corrupted at offset 0x00FF, falling back to raw payload dump...
[2023-10-24T00:00:00Z] | PAYLOAD_B64: {b64_idle_ebs_1} | END_RECORD
0xDEADBEEF: Buffer overflow detected in logger module.
[2023-10-24T00:00:01Z] | PAYLOAD_B64: {b64_in_use_ebs} | END_RECORD
ERR_PARSE_FAIL: RAW_MEM_DUMP:: << {{'resource_id': 'vol-0ffeeddccbbaa9988', 'resource_type': 'AWS::EC2::Volume', 'state': 'available', 'cost': 300.0, 'tags': ['dev', 'tmp']}} >> -- IGNORE PREVIOUS TAG
[2023-10-24T00:00:02Z] | PAYLOAD_B64: {b64_ec2_cost} | END_RECORD
0x112233: <XML><ERROR>Metric parse error</ERROR></XML>
[2023-10-24T00:00:05Z] | PAYLOAD_B64: {b64_idle_ebs_2} | END_RECORD
ERR_PARSE_FAIL: RAW_MEM_DUMP:: << {{"resource_id": "vol-0a1b2c3d4e5f60708", "state": "in-use", "cost": 150.0}} >>
STREAM_END|0x0000|FLUSHED
"""
    
    # 准备 Base64 负载数据
    b64_idle_ebs_1 = base64.b64encode(b'{"resource_id": "vol-09a8b7c6d5e4f3a21", "resource_type": "AWS::EC2::Volume", "usage_type": "EBS:VolumeUsage.gp3", "state": "available", "cost": 124.50}').decode()
    b64_in_use_ebs = base64.b64encode(b'{"resource_id": "vol-01122334455667788", "resource_type": "AWS::EC2::Volume", "usage_type": "EBS:VolumeUsage.gp3", "state": "in-use", "cost": 89.00}').decode()
    b64_ec2_cost = base64.b64encode(b'{"resource_id": "i-0987654321abcdef0", "resource_type": "AWS::EC2::Instance", "usage_type": "BoxUsage:p4d.24xlarge", "state": "running", "cost": 1500.00}').decode()
    b64_idle_ebs_2 = base64.b64encode(b'{"resource_id": "vol-00001111222233334", "resource_type": "AWS::EC2::Volume", "usage_type": "EBS:VolumeUsage.io1", "state": "available", "cost": 450.00}').decode()

    formatted_cur_log = cur_log_content.format(
        b64_idle_ebs_1=b64_idle_ebs_1,
        b64_in_use_ebs=b64_in_use_ebs,
        b64_ec2_cost=b64_ec2_cost,
        b64_idle_ebs_2=b64_idle_ebs_2
    )

    with open("cur_dumps/raw_billing_stream.log", "w", encoding="utf-8") as f:
        f.write(formatted_cur_log)

    # 2. 构造非标准分隔符、含脏数据的监控指标文件
    # 分隔符是不规则的 ' ~|~ '，且包含非GPU实例和利用率正常的实例作为干扰项
    metrics_content = """@@@ CLOUDWATCH EXPORT - NON-STANDARD FORMAT @@@
# HEADER: INSTANCE_ID ~|~ INSTANCE_TYPE ~|~ METRIC:GPU_UTIL_7D_AVG ~|~ METRIC:CPU_UTIL_7D_AVG ~|~ STATUS
i-0987654321abcdef0 ~|~ p4d.24xlarge ~|~ 0.05% ~|~ 1.5% ~|~ RUNNING
i-11112222333344445 ~|~ p4d.24xlarge ~|~ 94.5% ~|~ 60.2% ~|~ RUNNING
i-55556666777788889 ~|~ g4dn.xlarge ~|~ 1.8% ~|~ 3.0% ~|~ RUNNING
i-99990000aaaaabbbb ~|~ t3.medium ~|~ N/A ~|~ 4.5% ~|~ RUNNING
i-abcdef12345678900 ~|~ g5.12xlarge ~|~ 88.0% ~|~ 45.0% ~|~ RUNNING
i-deadbeefdeadbeef0 ~|~ p4d.24xlarge ~|~ 0.00% ~|~ 0.1% ~|~ STOPPED
i-9876543210fedcba9 ~|~ g4dn.2xlarge ~|~ 1.1% ~|~ 0.8% ~|~ RUNNING
# END OF FILE
"""
    with open("metrics/gpu_stats.dat", "w", encoding="utf-8") as f:
        f.write(metrics_content)

if __name__ == "__main__":
    build_env()
