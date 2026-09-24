import os
import json
import random
import string
import uuid

def rand_hex(length=16):
    return ''.join(random.choices(string.hexdigits.lower(), k=length))

def make_span(trace_id, span_id, parent_id, op, start, dur, tags=None, logs=None):
    s = {
        "traceID": trace_id,
        "spanID": span_id,
        "operationName": op,
        "startTime": start,
        "duration": dur
    }
    if parent_id:
        s["parentSpanID"] = parent_id
    if tags:
        s["tags"] = tags
    if logs:
        s["logs"] = logs
    return s

def generate_traces():
    all_spans = []
    base_time = 1698000000000000
    
    # Target Trace: Root duration > 5000000, has error, has payload
    target_trace_id = rand_hex(32)
    t_root = rand_hex(16)
    all_spans.append(make_span(
        target_trace_id, t_root, None, "frontend.checkout_gateway", 
        base_time, 5050000, 
        [{"key": "http.status_code", "type": "int64", "value": 504}]
    ))
    t_child1 = rand_hex(16)
    all_spans.append(make_span(
        target_trace_id, t_child1, t_root, "svc.order.orchestrator", 
        base_time + 1000, 5040000
    ))
    t_child2 = rand_hex(16)
    target_payload = "0x" + rand_hex(12)
    all_spans.append(make_span(
        target_trace_id, t_child2, t_child1, "grpc.inventory.ReserveStock", 
        base_time + 2000, 5035000,
        [{"key": "error", "type": "bool", "value": True}],
        [{
            "timestamp": base_time + 5035000,
            "fields": [
                {"key": "event", "type": "string", "value": "timeout"},
                {"key": "corrupted_payload", "type": "string", "value": target_payload}
            ]
        }]
    ))

    # Decoy 1: Root duration > 5000000, NO error, NO payload (Just a slow query)
    d1_trace_id = rand_hex(32)
    d1_root = rand_hex(16)
    all_spans.append(make_span(
        d1_trace_id, d1_root, None, "frontend.data_export", 
        base_time, 6200000, 
        [{"key": "http.status_code", "type": "int64", "value": 200}]
    ))
    d1_child = rand_hex(16)
    all_spans.append(make_span(
        d1_trace_id, d1_child, d1_root, "db.mysql.dump", 
        base_time + 500, 6190000,
        [{"key": "db.statement", "type": "string", "value": "SELECT * FROM huge_table"}]
    ))

    # Decoy 2: Has error and payload, but Root duration < 5000000
    d2_trace_id = rand_hex(32)
    d2_root = rand_hex(16)
    all_spans.append(make_span(
        d2_trace_id, d2_root, None, "frontend.user_profile", 
        base_time, 200000, 
        [{"key": "http.status_code", "type": "int64", "value": 500}]
    ))
    d2_child = rand_hex(16)
    all_spans.append(make_span(
        d2_trace_id, d2_child, d2_root, "svc.user.avatar", 
        base_time + 100, 190000,
        [{"key": "error", "type": "bool", "value": True}],
        [{
            "timestamp": base_time + 190000,
            "fields": [
                {"key": "event", "type": "string", "value": "crash"},
                {"key": "corrupted_payload", "type": "string", "value": "0xdeadbeef1234"}
            ]
        }]
    ))

    # Background Noise: 1000 normal traces (each with 1-4 spans)
    for _ in range(1000):
        tid = rand_hex(32)
        r_span = rand_hex(16)
        dur = random.randint(1000, 80000)
        all_spans.append(make_span(
            tid, r_span, None, random.choice(["api.get_items", "api.check_login", "api.ping"]), 
            base_time + random.randint(0, 100000), dur
        ))
        for _ in range(random.randint(0, 3)):
            c_span = rand_hex(16)
            all_spans.append(make_span(
                tid, c_span, r_span, random.choice(["redis.get", "db.query", "grpc.auth.Verify"]), 
                base_time + random.randint(100, 500), dur - 1000
            ))

    return all_spans

def build_env():
    os.makedirs("ops", exist_ok=True)
    base_dir = "traces_dump"
    os.makedirs(base_dir, exist_ok=True)

    # 1. Generate fragmented directory tree
    nodes = ["node_alpha", "node_beta", "node_gamma", "node_delta"]
    workers = ["w_01", "w_02", "w_03", "w_04"]
    mem_regions = ["0x00A", "0x00B", "0x00C", "0x00D", "0x00E"]
    
    dirs = []
    for n in nodes:
        for w in workers:
            for m in mem_regions:
                p = os.path.join(base_dir, n, w, m)
                os.makedirs(p, exist_ok=True)
                dirs.append(p)

    # 2. Get all spans and shuffle to simulate scattered memory
    all_spans = generate_traces()
    random.shuffle(all_spans)

    # 3. Distribute spans into files of different formats
    batch_size = 5
    for i in range(0, len(all_spans), batch_size):
        batch = all_spans[i:i+batch_size]
        target_dir = random.choice(dirs)
        fmt_choice = random.choice(["json", "jsonl", "log_corrupted"])
        
        file_id = rand_hex(8)
        if fmt_choice == "json":
            # standard json array
            with open(os.path.join(target_dir, f"spans_{file_id}.json"), "w", encoding="utf-8") as f:
                json.dump({"data": batch}, f)
        elif fmt_choice == "jsonl":
            # json lines format
            with open(os.path.join(target_dir, f"stream_{file_id}.jsonl"), "w", encoding="utf-8") as f:
                for s in batch:
                    f.write(json.dumps(s) + "\n")
        else:
            # log with prefix and json payload
            with open(os.path.join(target_dir, f"mem_dump_{file_id}.log"), "w", encoding="utf-8") as f:
                f.write(f"WARNING: MEMORY FLUSH AT {rand_hex(16)}\n")
                for s in batch:
                    f.write(f"RECOVERED_SPAN:: {json.dumps(s)}\n")
                f.write("END OF DUMP\n")

    # 4. Generate pure garbage noise files to break simple parsers
    for i in range(100):
        target_dir = random.choice(dirs)
        with open(os.path.join(target_dir, f"garbage_{rand_hex(4)}.tmp"), "w", encoding="utf-8") as f:
            f.write("Goroutine stack dump:\n")
            f.write("SIGSEGV: segmentation violation\n")
            f.write("PC=0x45a9b1 m=4 sigcode=1\n")
            f.write("... " + rand_hex(64) + " ...\n")
            # a fake span that is completely broken JSON
            f.write('{"traceID": "' + rand_hex(32) + '", "spanID": "broken, "duration": 9999999\n')

if __name__ == "__main__":
    build_env()
