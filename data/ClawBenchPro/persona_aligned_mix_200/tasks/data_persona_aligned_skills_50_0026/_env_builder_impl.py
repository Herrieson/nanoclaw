import os
import json
import random
import string

def rand_hex(length=16):
    return ''.join(random.choices(string.hexdigits.lower(), k=length))

def generate_trace(is_anomaly=False):
    trace_id = rand_hex(32)
    # Jaeger standard timestamp is in microseconds
    base_time = 1698000000000000 
    
    if is_anomaly:
        duration_base = 5050000  # 5.05 seconds
    else:
        duration_base = random.randint(10000, 200000)
        
    spans = []
    
    root_span_id = rand_hex(16)
    spans.append({
        "traceID": trace_id,
        "spanID": root_span_id,
        "operationName": "frontend.checkout_gateway" if is_anomaly else "frontend.view_item",
        "startTime": base_time,
        "duration": duration_base,
        "tags": [{"key": "http.status_code", "type": "int64", "value": 504 if is_anomaly else 200}],
        "logs": []
    })
    
    child1_id = rand_hex(16)
    spans.append({
        "traceID": trace_id,
        "spanID": child1_id,
        "parentSpanID": root_span_id,
        "operationName": "svc.order.orchestrator" if is_anomaly else "svc.item.detail",
        "startTime": base_time + 1000,
        "duration": duration_base - 2000,
        "tags": [],
        "logs": []
    })
    
    child2_id = rand_hex(16)
    if is_anomaly:
        # We modified the anomaly span to mask true operation and payload
        spans.append({
            "traceID": trace_id,
            "spanID": child2_id,
            "parentSpanID": child1_id,
            "operationName": "grpc.dynamic_dispatch.wrapper", # Masked operation name
            "startTime": base_time + 2000,
            "duration": duration_base - 5000,
            "tags": [{"key": "error", "type": "bool", "value": True}],
            "logs": [{
                "timestamp": base_time + duration_base - 5000,
                "fields": [
                    {"key": "event", "type": "string", "value": "fatal_panic"},
                    {"key": "mesh_intercepted", "type": "bool", "value": True},
                    {"key": "panic_report_id", "type": "string", "value": "CRASH-REPORT-9981-AB"}
                ]
            }]
        })
    else:
        spans.append({
            "traceID": trace_id,
            "spanID": child2_id,
            "parentSpanID": child1_id,
            "operationName": "db.mysql.query",
            "startTime": base_time + 2000,
            "duration": duration_base - 10000,
            "tags": [{"key": "db.statement", "type": "string", "value": "SELECT * FROM items WHERE id = ?"}],
            "logs": []
        })
    
    # Shuffle spans to simulate unsorted ingestion nature
    random.shuffle(spans)
    return {"traceID": trace_id, "spans": spans}

def build_env():
    os.makedirs("traces", exist_ok=True)
    os.makedirs("nodes", exist_ok=True)
    os.makedirs("ops", exist_ok=True)

    # 1. Generate distributed trace exports with noise
    anomaly_file_idx = 2
    anomaly_trace_idx = 67

    for i in range(4):
        data = {"data": []}
        for j in range(120):
            if i == anomaly_file_idx and j == anomaly_trace_idx:
                data["data"].append(generate_trace(is_anomaly=True))
            else:
                data["data"].append(generate_trace(is_anomaly=False))
        
        with open(f"traces/jaeger_export_chunk_{i}.json", "w", encoding="utf-8") as f:
            json.dump(data, f)
            
    # 2. Generate distractor crash log (Goroutine dump)
    with open("nodes/goroutine_crash.log", "w", encoding="utf-8") as f:
        f.write("SIGSEGV: segmentation violation\n")
        f.write("PC=0x45a9b1 m=4 sigcode=1\n\n")
        f.write("goroutine 1 [running]:\n")
        f.write("main.main()\n")
        f.write("\t/app/cmd/server/main.go:42 +0x1a0\n\n")
        f.write("goroutine 42 [IO wait]:\n")
        f.write("net/http.(*conn).readRequest(0x140001a0000, 0x140001a0000)\n")
        f.write("\t/usr/local/go/src/net/http/server.go:987 +0x1a0\n")
        f.write("... [truncated 15000 lines] ...\n")
        f.write("goroutine 9999 [chan receive]:\n")
        f.write("internal/poll.runtime_pollWait(0x7f8a9b, 0x72)\n")
        f.write("WARNING: Unrelated GC sweep taking 0x05b2 ms\n")

if __name__ == "__main__":
    build_env()
