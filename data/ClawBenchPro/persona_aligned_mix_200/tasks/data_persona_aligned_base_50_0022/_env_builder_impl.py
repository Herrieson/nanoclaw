import os
import json
import random
import datetime

def generate_hex_dump():
    return " ".join([f"{random.randint(0, 255):02X}" for _ in range(16)])

def build_env():
    # 确保在当前执行目录（已经被沙盒设定为 assets/data_persona_aligned_base_50_0022/）下创建所需文件夹
    os.makedirs("farm_logs", exist_ok=True)
    os.makedirs("scene_data", exist_ok=True)
    
    # 定义干扰项和目标项
    target_broken_node = "SHD_Flesh_Subsurface_09"
    target_missing_texture = "/prod/show/SC043/assets/chars/mutant/tex/v003/diffuse_UDIM_1001.tx"
    
    # 1. 生成农场渲染日志 (farm_logs)
    # 大部分是正常或带有无关警告的日志
    for i in range(1, 31):
        log_name = f"farm_logs/node_{i:03d}.log"
        with open(log_name, "w", encoding="utf-8") as f:
            base_time = datetime.datetime(2023, 10, 27, 3, 0, 0)
            f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S.000')}] [INFO] Initializing RenderMan Engine...\n")
            f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S.042')}] [INFO] Loading scene graph from SC043_v099_graph.json\n")
            
            # 制造一些干扰警告
            if random.random() > 0.5:
                f.write(f"[{base_time.strftime('%Y-%m-%d %H:%M:%S.105')}] [WARNING] Shader SHD_Eye_01 missing specular map, using default.\n")
                
            # 只有特定的几台机器出现致命崩溃
            if i in [7, 14, 23]:
                crash_time = base_time + datetime.timedelta(minutes=random.randint(5, 15), seconds=random.randint(1, 59))
                f.write(f"[{crash_time.strftime('%Y-%m-%d %H:%M:%S.823')}] [DEBUG] Evaluating shading network for tile (12, 45)...\n")
                f.write(f"[{crash_time.strftime('%Y-%m-%d %H:%M:%S.824')}] [ERROR] Extracted minidump at hex 0x7FFA8C33010\n")
                for _ in range(5):
                    f.write(f"    0x7FFF: {generate_hex_dump()} - memory unmapped\n")
                f.write(f"[{crash_time.strftime('%Y-%m-%d %H:%M:%S.825')}] [FATAL] Segmentation fault in shading evaluator. Node <{target_broken_node}> caused a memory violation during texture fetch.\n")
                f.write(f"[{crash_time.strftime('%Y-%m-%d %H:%M:%S.826')}] [INFO] Core dumped to /var/crash/render_core_{i}.dmp\n")
            else:
                success_time = base_time + datetime.timedelta(minutes=20)
                f.write(f"[{success_time.strftime('%Y-%m-%d %H:%M:%S.000')}] [INFO] Tile rendering completed successfully.\n")

    # 2. 生成深度嵌套的场景拓扑图 (scene_data/SC043_v099_graph.json)
    # 创建一个极度嵌套、包含大量干扰数据的 JSON
    def generate_shader_node(name, is_target=False):
        if is_target:
            diffuse = target_missing_texture
        else:
            diffuse = f"/prod/show/SC043/assets/generic/tex/v001/{name}_diff.tx"
            
        return {
            "type": "SurfaceShader",
            "metadata": {
                "author": "td_bot",
                "version": random.randint(1, 10),
                "timestamp": 1698350000 + random.randint(1, 1000)
            },
            "connections": {
                "inputs": {
                    "diffuse_map": diffuse,
                    "roughness_map": f"/prod/show/SC043/assets/generic/tex/v001/{name}_rough.tx",
                    "normal_map": f"/prod/show/SC043/assets/generic/tex/v001/{name}_nrm.tx",
                    "sss_weight": random.random()
                },
                "outputs": {
                    "outColor": f"{name}.outColor",
                    "outAlpha": f"{name}.outAlpha"
                }
            }
        }

    # 构建层级树
    scene_graph = {
        "scene": {
            "version": "SC043_v099",
            "fps": 24,
            "render_settings": {
                "resolution": [4096, 2160],
                "pixel_aspect": 1.0,
                "engine": "RenderMan"
            },
            "hierarchy": {
                "world": {
                    "transform": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
                    "children": {
                        "environment": {"type": "group", "children": {}},
                        "characters": {
                            "type": "group",
                            "children": {}
                        }
                    }
                }
            }
        }
    }

    # 填充大量角色和着色器干扰项
    char_group = scene_graph["scene"]["hierarchy"]["world"]["children"]["characters"]["children"]
    
    for c in range(1, 11):
        char_name = f"Character_{c:02d}"
        shading_group = {}
        for s in range(1, 15):
            shader_name = f"SHD_Char_{c:02d}_Mat_{s:02d}"
            shading_group[shader_name] = generate_shader_node(shader_name)
            
        char_group[char_name] = {
            "type": "mesh",
            "visibility": True,
            "shading_network": {
                "nodes": shading_group
            }
        }
        
    # 注入目标错误节点及其层级
    target_char = "Mutant_Hero_01"
    target_shading_group = {}
    
    # 放入目标节点
    target_shading_group[target_broken_node] = generate_shader_node(target_broken_node, is_target=True)
    
    # 放入一些跟目标节点在同一个组里的干扰节点
    for s in range(1, 10):
        fake_name = f"SHD_Flesh_Subsurface_{s:02d}"
        if fake_name != target_broken_node:
            target_shading_group[fake_name] = generate_shader_node(fake_name)
            
    char_group[target_char] = {
        "type": "mesh",
        "visibility": True,
        "shading_network": {
            "nodes": target_shading_group
        }
    }

    # 写入复杂的 JSON 文件
    with open("scene_data/SC043_v099_graph.json", "w", encoding="utf-8") as f:
        json.dump(scene_graph, f, indent=2)

if __name__ == "__main__":
    build_env()
