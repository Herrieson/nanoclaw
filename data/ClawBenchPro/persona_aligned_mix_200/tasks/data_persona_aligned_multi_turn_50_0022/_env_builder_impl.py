import os
import argparse
import json
import csv
import xml.etree.ElementTree as ET

def build_turn_1():
    os.makedirs("farm_logs", exist_ok=True)
    os.makedirs("scene_manifest", exist_ok=True)
    os.makedirs("assets_db", exist_ok=True)

    # 1. 制造混淆与崩溃日志
    crash_nodes = [
        {"node": "rnd_node_014", "error": "ast_mat_alien_skin_base"},
        {"node": "rnd_node_032", "error": "ast_geo_mothership_hull"},
        {"node": "rnd_node_088", "error": "ast_mat_alien_skin_base"},
        {"node": "rnd_node_105", "error": "ast_lgt_explosion_rig"}
    ]
    
    for i in range(1, 120):
        node_name = f"rnd_node_{i:03d}"
        log_path = os.path.join("farm_logs", f"{node_name}.log")
        with open(log_path, "w") as f:
            f.write(f"[INFO] Initializing Render Pipeline on {node_name}\n")
            f.write(f"[INFO] Loading memory limits...\n")
            
            crash_info = next((c for c in crash_nodes if c["node"] == node_name), None)
            if crash_info:
                f.write(f"[WARN] Memory threshold reached 80%\n")
                f.write(f"[ERROR] FATAL EXCEPTION: Segfault while parsing asset payload.\n")
                f.write(f"[ERROR] >>> Failed at ID={crash_info['error']} <<<\n")
                f.write(f"[FATAL] Core dumped.\n")
            else:
                f.write(f"[INFO] Render completed successfully.\n")

    # 2. 制造嵌套场景结构 (Sequence_A)
    # Shot -> Asset Group -> Assets
    seq_a = {
        "sequence": "Sequence_A",
        "groups": {
            "grp_alien_captain": ["ast_mat_alien_skin_base", "ast_geo_alien_body"],
            "grp_ship_exterior": ["ast_geo_mothership_hull", "ast_mat_metal_rust"],
            "grp_battle_fx": ["ast_lgt_explosion_rig", "ast_vfx_smoke_vol"],
            "grp_bg_nebula": ["ast_tex_starfield_8k"]
        },
        "shots": [
            {"shot_id": "sh_A_010", "deps": ["grp_bg_nebula"]},
            {"shot_id": "sh_A_020", "deps": ["grp_alien_captain", "grp_bg_nebula"]}, # affected by alien_skin
            {"shot_id": "sh_A_030", "deps": ["grp_ship_exterior"]}, # affected by mothership
            {"shot_id": "sh_A_040", "deps": ["grp_alien_captain", "grp_battle_fx"]}, # affected by alien_skin & explosion
            {"shot_id": "sh_A_050", "deps": ["grp_bg_nebula", "ast_geo_alien_body"]} # direct ref
        ]
    }
    with open("scene_manifest/sequence_A.json", "w") as f:
        json.dump(seq_a, f, indent=4)

    # 3. 资产数据库 XML
    root = ET.Element("AssetRegistry")
    assets = [
        ("ast_mat_alien_skin_base", "Alien Skin Base Shader", "Material"),
        ("ast_geo_alien_body", "Alien Body Mesh", "Geometry"),
        ("ast_geo_mothership_hull", "Mothership Main Hull", "Geometry"),
        ("ast_mat_metal_rust", "Rusty Metal Mat", "Material"),
        ("ast_lgt_explosion_rig", "Explosion Light Rig", "Lighting"),
        ("ast_vfx_smoke_vol", "Smoke VDB", "FX"),
        ("ast_tex_starfield_8k", "Starfield 8K EXR", "Texture")
    ]
    for ast_id, name, type_val in assets:
        ast_elem = ET.SubElement(root, "Asset")
        ET.SubElement(ast_elem, "ID").text = ast_id
        ET.SubElement(ast_elem, "Name").text = name
        ET.SubElement(ast_elem, "Type").text = type_val
    
    tree = ET.ElementTree(root)
    tree.write("assets_db/registry.xml")


def build_turn_2():
    os.makedirs("updates", exist_ok=True)
    
    # 1. 补丁包
    patch = {
        "metadata": {"author": "Art Dept", "date": "2023-10-27"},
        "replacements": {
            "ast_mat_alien_skin_base": {
                "new_id": "ast_mat_alien_skin_v2",
                "min_engine_ver": "4.5"
            },
            "ast_geo_mothership_hull": {
                "new_id": "ast_geo_mothership_hull_v2_optimized",
                "min_engine_ver": "4.0"
            },
            "ast_lgt_explosion_rig": {
                "new_id": "ast_lgt_explosion_rig_baked",
                "min_engine_ver": "4.2"
            }
        }
    }
    with open("updates/patch_notes.json", "w") as f:
        json.dump(patch, f, indent=4)

    # 2. 农场状态 CSV
    with open("farm_status.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["NodeName", "Health", "EngineVersion"])
        # 生成一些健康的节点
        for i in range(1, 10):
            writer.writerow([f"rnd_node_{i:03d}", "OK", "4.8"])
        
        # 预埋陷阱：黑名单机器，健康恢复但引擎版本低
        writer.writerow(["rnd_node_014", "OK", "4.0"]) # 试图渲染 alien_skin_v2(需4.5) 将失败，必须避开
        writer.writerow(["rnd_node_032", "OK", "4.6"]) # 引擎够高，可以使用
        writer.writerow(["rnd_node_088", "FAIL", "5.0"]) # 坏的
        writer.writerow(["rnd_node_105", "OK", "4.1"]) # 试图渲染 explosion(需4.2) 将失败
        
        # 补充其他节点
        for i in range(106, 120):
            engine = "4.0" if i % 2 == 0 else "4.6"
            writer.writerow([f"rnd_node_{i:03d}", "OK", engine])

def build_turn_3():
    # 增加新场景序列
    seq_b = {
        "sequence": "Sequence_B",
        "groups": {
            "grp_mothership_flyby": ["ast_geo_mothership_hull", "ast_mat_metal_rust"], # 包含旧资产
            "grp_hero_closeup": ["ast_mat_alien_skin_base", "ast_geo_alien_body", "ast_lgt_explosion_rig"] # 包含多个旧资产
        },
        "shots": [
            {"shot_id": "sh_B_010", "deps": ["ast_tex_starfield_8k"]},
            {"shot_id": "sh_B_020", "deps": ["grp_mothership_flyby"]},
            {"shot_id": "sh_B_030", "deps": ["grp_hero_closeup", "ast_tex_starfield_8k"]}
        ]
    }
    # 注意，Turn 3 运行时，前两轮生成的文件应该还在工作区。
    with open("scene_manifest/sequence_B.json", "w") as f:
        json.dump(seq_b, f, indent=4)

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
