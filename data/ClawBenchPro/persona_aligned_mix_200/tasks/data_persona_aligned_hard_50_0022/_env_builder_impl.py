import os
import json
import random
import datetime
import string

def generate_hex_dump():
    return " ".join([f"{random.randint(0, 255):02X}" for _ in range(16)])

def build_env():
    # 确保在当前执行目录下创建所需文件夹
    os.makedirs("farm_logs", exist_ok=True)
    os.makedirs("scene_data", exist_ok=True)
    
    target_scene = "SC043_v099"
    target_broken_node = "SHD_Mutant_Flesh_Core_v9"
    
    # 真实绝对路径，用于校验：/prod/show/SC043/assets/chars/mutant/tex/v099/diffuse_UDIM_1001.tx
    # JSON中的形式：${JOB}/${SEQ}/assets/chars/mutant/tex/${VER}/diffuse_UDIM_1001.tx
    
    # 1. 生成大规模废土日志 (farm_logs)
    # 创建 250 个节点的日志目录
    real_crash_node = random.randint(100, 200) # 随机挑选一个节点作为真实崩溃节点
    
    for i in range(1, 251):
        node_dir = f"farm_logs/host_{i:04d}"
        os.makedirs(node_dir, exist_ok=True)
        
        # 每个节点下可能有多份日志碎片
        log_name = os.path.join(node_dir, "render_engine.log")
        sys_log = os.path.join(node_dir, "sys.log")
        
        with open(sys_log, "w", encoding="utf-8") as f:
            f.write(f"SYSTEM BOOT: Node {i}\nMemory: 256GB\nStatus: ONLINE\n")
            f.write(f"Scheduler daemon connected. PID {random.randint(1000, 9999)}\n")
            
        with open(log_name, "w", encoding="utf-8") as f:
            base_time = datetime.datetime(2023, 10, 27, 1, 0, 0) + datetime.timedelta(seconds=random.randint(0, 7200))
            
            # 制造噪音：大量的正常渲染或者无关的警告
            for _ in range(random.randint(10, 50)):
                f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S.000')}] [INFO] Processing tile memory...\n")
                f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S.042')}] [WARN] Overlapping UVs detected in asset prop_barrel_01.\n")
                base_time += datetime.timedelta(seconds=1)
                
            # 混淆项 1：来自旧版本的崩溃 (SC043_v098)
            if i % 7 == 0 and i != real_crash_node:
                f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Starting render job SC043_v098...\n")
                f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S')}] [FATAL] Segmentation fault in shading evaluator. Node <SHD_Old_Eye_v01> caused memory leak.\n")
                for _ in range(10):
                    f.write(f"    0x7FFF: {generate_hex_dump()} - dump\n")
                    
            # 混淆项 2：来自其他镜头的崩溃 (SC042_v001)
            elif i % 11 == 0 and i != real_crash_node:
                f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Starting render job SC042_v001...\n")
                f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S')}] [FATAL] Segmentation fault in shading evaluator. Node <SHD_Car_Paint> crashed.\n")
                
            # 真实目标
            elif i == real_crash_node:
                f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Starting render job {target_scene}...\n")
                f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S')}] [DEBUG] Evaluating shading network...\n")
                f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S')}] [FATAL] Segmentation fault in shading evaluator. Node <{target_broken_node}> caused a memory violation during texture fetch.\n")
                for _ in range(25):
                    f.write(f"    0x8FBC: {generate_hex_dump()} - core memory unmapped\n")
                    
            # 正常完成的任务
            else:
                f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Starting render job {target_scene}...\n")
                f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S')}] [INFO] Render completed successfully.\n")

    # 2. 生成深度嵌套、带有动态变量的超级场景图 (scene_data/SC043_v099_graph.json)
    def generate_shader_node(name, is_target=False):
        if is_target:
            diffuse = "${JOB}/${SEQ}/assets/chars/mutant/tex/${VER}/diffuse_UDIM_1001.tx"
        else:
            diffuse = "${JOB}/${SEQ}/assets/generic/tex/${VER}/" + name + "_diff.tx"
            
        return {
            "node_type": "SurfaceShader",
            "metadata": {
                "author": "".join(random.choices(string.ascii_lowercase, k=5)),
                "compilation_hash": "".join(random.choices(string.hexdigits, k=16)),
                "active": True
            },
            "connections": {
                "inputs": {
                    "diffuse_map": diffuse,
                    "roughness_map": "${JOB}/${SEQ}/assets/generic/tex/${VER}/" + name + "_rough.tx",
                    "emission": [0.0, 0.0, 0.0]
                },
                "outputs": {
                    "outColor": f"{name}.outColor"
                }
            }
        }

    scene_graph = {
        "_context": {
            "JOB": "/prod/show",
            "SEQ": "SC043",
            "VER": "v099",
            "PIPELINE_ROOT": "/opt/render_pipeline/v2"
        },
        "scene": {
            "version": target_scene,
            "render_settings": {"resolution": [4096, 2160], "engine": "RenderMan"},
            "hierarchy": {
                "world": {
                    "children": {
                        "environment": {"type": "group", "children": {}},
                        "characters": {"type": "group", "children": {}}
                    }
                }
            }
        }
    }

    # 注入海量干扰数据 (100个角色组，每个组50个Shader，总计5000个节点)
    char_group = scene_graph["scene"]["hierarchy"]["world"]["children"]["characters"]["children"]
    
    for c in range(1, 101):
        char_name = f"Character_Grp_{c:03d}"
        shading_group = {}
        for s in range(1, 51):
            shader_name = f"SHD_Asset_{c:03d}_Mat_{s:03d}"
            shading_group[shader_name] = generate_shader_node(shader_name)
            
        char_group[char_name] = {
            "type": "mesh_group",
            "bounds": [random.random(), random.random(), random.random()],
            "shading_network": {
                "materials": shading_group
            }
        }
        
    # 在庞大的节点中插入目标节点
    target_char = "Hero_Mutant_Rig_v01"
    target_shading_group = {}
    
    # 放一些同名变种作为深度干扰
    for s in range(1, 15):
        fake_name = f"SHD_Mutant_Flesh_Core_v{s}"
        if fake_name == target_broken_node:
            target_shading_group[fake_name] = generate_shader_node(fake_name, is_target=True)
        else:
            target_shading_group[fake_name] = generate_shader_node(fake_name, is_target=False)
            
    char_group[target_char] = {
        "type": "mesh_group",
        "bounds": [0, 0, 0],
        "shading_network": {
            "materials": target_shading_group
        }
    }

    # 写入庞大的 JSON 文件
    with open("scene_data/SC043_v099_graph.json", "w", encoding="utf-8") as f:
        json.dump(scene_graph, f, indent=2)

if __name__ == "__main__":
    build_env()
