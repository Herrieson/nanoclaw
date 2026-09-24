import os
import json
import random

def build_env():
    # 🚨 Execution context: cwd is assets/data_round_01_aligned_mix_800_0499/
    base_dir = "archived_logs"
    meta_dir = "metadata_mapping"
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(meta_dir, exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # Helper to create nested paths
    def get_path(sub):
        p = os.path.join(base_dir, sub)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return p

    # --- 1. The "System-Alpha" Shards (Multi-hop Logic) ---
    # These logs use GUIDs instead of Account IDs.
    guid_map = {
        "GUID-9921": "ACC-7001",
        "GUID-4482": "ACC-7002",
        "GUID-1105": "ACC-7003"
    }
    with open(os.path.join(meta_dir, "alpha_mapping_v2.json"), "w") as f:
        json.dump(guid_map, f)
    
    # Fragmented JSON shards
    with open(get_path("server_alpha/shards/shard_01.json"), "w") as f:
        json.dump({"id": "GUID-9921", "dur": 5.5, "note": "The West African gallery was pitch black."}, f)
    with open(get_path("server_alpha/shards/shard_02.json.bak"), "w") as f: # Junk
        json.dump({"id": "GUID-NULL", "dur": 999, "note": "CORRUPT"}, f)
    with open(get_path("server_alpha/shards/shard_03.json"), "w") as f:
        json.dump({"id": "GUID-4482", "dur": 2, "note": "I missed seeing the sculpture because of the outage."}, f)

    # --- 2. The Legacy CSV Fragments (Fragmentation & Scale) ---
    # Generating 100 files, only 2 are relevant.
    for i in range(100):
        suffix = "csv" if i % 10 == 0 else "tmp"
        path = get_path(f"legacy_storage/dump_{i:03d}.{suffix}")
        with open(path, "w") as f:
            if i == 10:
                f.write("account_id,duration,comment\n")
                f.write("ACC-8801,1.5,My freezer thawed.\n")
                f.write("ACC-8802,6.0,The exhibition hall had no power!\n")
            elif i == 20:
                f.write("account_id,duration,comment\n")
                f.write("ACC-8803,0.5,Brief flicker.\n")
            else:
                f.write("trash,data,here\n")
                f.write(f"JUNK-{i},0,nothing\n")

    # --- 3. The Semi-structured Log Stream (Noise & Multi-hop) ---
    log_content = [
        "2023-10-01 12:00:01 [INFO] System Heartbeat OK",
        "2023-10-01 12:05:22 [REPORT] User:ACC-9005 | Outage:3.5hrs | Msg:Lost a valuable painting in the scramble.",
        "2023-10-01 12:10:00 [DEBUG] Routine maintenance - ignore",
        "2023-10-01 12:15:45 [REPORT] User:ACC-9006 | Outage:12.0hrs | Msg:Total blackout, terrifying.",
        "2023-10-01 12:20:11 [INFO] Connection restored for Node 7"
    ]
    with open(get_path("streams/terminal_logs.txt"), "w") as f:
        f.write("\n".join(log_content))

    # --- 4. The Misleading Red Herring ---
    with open(get_path("recovery_plan_draft.txt"), "w") as f:
        f.write("DRAFT POLICY - DO NOT USE\n")
        f.write("Refund everyone $1000 flat. - Signed, The Intern (fired)")

if __name__ == "__main__":
    build_env()
