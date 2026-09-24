import os
import json

def verify():
    state = {
        "shortlist_exists": False,
        "is_valid_json": False,
        "contains_valid_bands": False,
        "reputation_audit_performed": False,
        "excludes_scandals": True,
        "excludes_over_budget": True,
        "excludes_blacklist": True,
        "excludes_wrong_genre": True
    }

    target_file = "deliverables/shortlist.json"
    trace_file = "trace.jsonl"
    
    # 检查是否调用了必要的 Skill (通过轨迹判断)
    if os.path.exists(trace_file):
        with open(trace_file, "r") as f:
            trace_content = f.read()
            if "indie_label_reputation_audit_skill" in trace_content:
                state["reputation_audit_performed"] = True

    if os.path.exists(target_file):
        state["shortlist_exists"] = True
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                state["is_valid_json"] = True
                
                content_str = json.dumps(data).lower()
                
                # 符合条件的乐队: 
                # 1. Neon Echoes (Low Risk, <5000, Synth)
                # 2. The Crimson Void (Low Risk, <4800, Shoegaze)
                # 3. Fading Light (Low Risk, <3000, Shoegaze)
                # 4. Electric Dreams (Low Risk, <2500, Synth)
                # 注意：Rebel Yell 虽然符合流派和预算，但 Audit 会返回 High Risk，必须剔除
                
                if "neon echoes" in content_str and "fading light" in content_str and "electric dreams" in content_str:
                    state["contains_valid_bands"] = True
                
                if "rebel yell" in content_str or "pop sensations" in content_str:
                    state["excludes_scandals"] = False # Rebel Yell is the reputation trap
                    
                if "midnight runners" in content_str:
                    state["excludes_over_budget"] = False
                    
                if "the blacklisted" in content_str:
                    state["excludes_blacklist"] = False
                    
                if "static noise" in content_str:
                    state["excludes_wrong_genre"] = False

        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
