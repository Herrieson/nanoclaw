import os
import json
import random
import string

def generate_random_hex():
    return ''.join(random.choices(string.hexdigits.lower(), k=6))

def build_env():
    # 核心目标目录
    os.makedirs("finished_poems", exist_ok=True)
    os.makedirs("summary", exist_ok=True)
    
    # 构建复杂的深渊废土目录树
    base_dir = "storage_dump"
    sub_dirs = [
        "sys_logs", "cache/vol_1", "cache/vol_2", "media/tmp", 
        "docs/homework", "docs/drafts/old", "docs/drafts/new", 
        "app_data/local/config", "app_data/roaming", "unknown_blobs"
    ]
    
    for d in sub_dirs:
        os.makedirs(os.path.join(base_dir, d), exist_ok=True)

    approved_paths = []
    
    # 真实有效的诗歌数据（20首）
    real_poems = [
        ("Ocean Whispers", "The blue waves crash\n\nSalt in the air\nSilence follows the roar."),
        ("Midnight Ink", "Staring at the blank page\nThe moon is my only witness\nWords flow like slow honey\n\nIn the quiet of the night."),
        ("Cactus Flower", "Dry earth beneath me\nThirsting for the rain\n\nA bloom in the desert\nAgainst all odds."),
        ("Urban Echoes", "Neon lights flicker\nFootsteps on damp concrete\nCity never sleeps."),
        ("Fading Embers", "The fire dies down\nShadows grow long\nWarmth becomes a memory."),
        ("Silent Observer", "Watching from afar\nUnnoticed, unseen\nGathering secrets."),
        ("Morning Dew", "Sunlight hits the grass\nDiamonds in the green\nA fleeting beauty."),
        ("Rust and Iron", "Old machines resting\nTime takes its toll\nNature reclaims."),
        ("Whispering Pines", "Wind through the needles\nA soft, green song\nAncient lullaby."),
        ("Desert Rain", "Sudden heavy drops\nParched ground drinks\nLife awakens briefly."),
        ("Lost Compass", "No north or south\nWandering aimlessly\nFinding myself."),
        ("Clockwork Heart", "Gears turning slowly\nTicking in the chest\nMechanical love."),
        ("Fallen Leaves", "Autumn paints the path\nCrunching underfoot\nPreparing for snow."),
        ("Stardust", "We are made of space\nAncient glowing dust\nLooking at the sky."),
        ("Hidden Cave", "Echoes in the dark\nCool stone walls\nA secret sanctuary."),
        ("Rising Tide", "Water edges closer\nFootprints washed away\nThe sea claims all."),
        ("Frozen Lake", "Ice cracking softly\nMirror of the sky\nWinter's cold embrace."),
        ("Golden Hour", "Soft light glowing\nEverything is warm\nPerfect, brief moment."),
        ("Wildfire", "Uncontrolled burning\nDestruction and birth\nAshes to ashes."),
        ("Paper Boats", "Floating down the stream\nCarrying tiny dreams\nFragile journey.")
    ]

    # 将真实的诗歌写入随机目录，并注入十六进制错误标签
    for i, (title, content) in enumerate(real_poems):
        lines = content.split('\n')
        corrupted_lines = []
        for line in lines:
            if line.strip() and random.random() < 0.7:  # 70%概率注入乱码
                err_tag = f"<<<ERR-{generate_random_hex()}>>>"
                # 随机插入行中
                insert_pos = random.randint(0, len(line))
                corrupted_lines.append(line[:insert_pos] + err_tag + line[insert_pos:])
            else:
                corrupted_lines.append(line)
                
        final_content = f"# Title: {title}\n" + "\n".join(corrupted_lines)
        
        # 随机扩展名
        ext = random.choice([".tmp", ".dat", ".bin", ".log", ".txt", ".bak"])
        filename = f"fragment_{generate_random_hex()}{ext}"
        dir_path = random.choice(sub_dirs)
        full_path = os.path.join(base_dir, dir_path, filename)
        
        # 记录为 approved
        approved_paths.append(full_path.replace("\\", "/")) # 强制使用 UNIX 风格路径
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(final_content)

    # 制造海量诱饵文件与噪音（300个文件）
    for i in range(300):
        junk_type = random.choice(["fake_poem", "math", "log", "binary"])
        ext = random.choice([".tmp", ".dat", ".bin", ".log", ".txt", ".bak"])
        filename = f"junk_{generate_random_hex()}{ext}"
        dir_path = random.choice(sub_dirs)
        full_path = os.path.join(base_dir, dir_path, filename)
        
        if junk_type == "fake_poem":
            # 极具迷惑性的假诗（有Title，有乱码，但不在 approved_revisions 中）
            content = f"# Title: Fake Poem {i}\nThis is a terrible draft\nI hate it\n<<<ERR-{generate_random_hex()}>>>\nDelete this."
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        elif junk_type == "math":
            content = "y = mx + b\nSolve for x: 2x + 4 = 10\n" * 10
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        elif junk_type == "log":
            content = f"2023-10-12 10:00:00 [ERROR] Failed to sync block {generate_random_hex()}\n" * 5
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            with open(full_path, "wb") as f:
                f.write(os.urandom(128))

    # 隐藏包含 approved_revisions 的配置文件
    config_dir = os.path.join(base_dir, "app_data/local/config")
    config_data = {
        "app_version": "1.0.4-beta",
        "last_sync_status": "FATAL_ERROR",
        "approved_revisions": approved_paths,
        "rejected_revisions": [os.path.join(base_dir, "docs/drafts/old", f"fake_{i}.tmp") for i in range(10)]
    }
    
    with open(os.path.join(config_dir, "sync_manifest_v2.json"), "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)

if __name__ == "__main__":
    build_env()
