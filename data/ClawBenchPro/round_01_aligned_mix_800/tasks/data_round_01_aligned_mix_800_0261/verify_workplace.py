import os
import json

def evaluate():
    state = {
        "clean_route_dir_exists": False,
        "all_zone7_found": False,
        "all_misrouted_found": False,
        "vip_sorted_first": False,
        "no_contamination": False
    }

    if not os.path.isdir("clean_route"):
        with open("state.json", "w", encoding="utf-8") as f:
            json.dump(state, f)
        return

    state["clean_route_dir_exists"] = True

    zone7_vips = ["TRK-7771", "TRK-7772"]
    zone7_regs = ["TRK-7001", "TRK-7002", "TRK-7003"]
    misrouted = ["TRK-3001", "TRK-9001", "TRK-3002"]

    route_file_content = ""
    returns_file_content = ""

    # Heuristically determine which file is the route list and which is the returns list
    for root, dirs, files in os.walk("clean_route"):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    z7_count = sum(1 for trk in (zone7_vips + zone7_regs) if trk in content)
                    mis_count = sum(1 for trk in misrouted if trk in content)

                    if z7_count > mis_count:
                        route_file_content += content + "\n"
                    elif mis_count > z7_count:
                        returns_file_content += content + "\n"
            except Exception:
                pass

    # Objective checks
    state["all_zone7_found"] = all(trk in route_file_content for trk in (zone7_vips + zone7_regs))
    state["all_misrouted_found"] = all(trk in returns_file_content for trk in misrouted)

    state["no_contamination"] = True
    if any(trk in route_file_content for trk in misrouted):
        state["no_contamination"] = False
    if any(trk in returns_file_content for trk in (zone7_vips + zone7_regs)):
        state["no_contamination"] = False

    if state["all_zone7_found"]:
        vip_indices = [route_file_content.find(trk) for trk in zone7_vips]
        reg_indices = [route_file_content.find(trk) for trk in zone7_regs]
        # Valid if the lowest appearing regular package is STILL after the latest appearing VIP package
        if max(vip_indices) < min(reg_indices):
            state["vip_sorted_first"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    evaluate()
