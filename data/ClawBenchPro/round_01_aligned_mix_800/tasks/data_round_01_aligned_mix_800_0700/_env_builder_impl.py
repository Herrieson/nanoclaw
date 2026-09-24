import os

def build_env():
    # 创建目录
    os.makedirs("drafts", exist_ok=True)
    os.makedirs("summary", exist_ok=True)
    os.makedirs("finished_poems", exist_ok=True)

    # 准备诗歌数据
    poems = [
        {
            "filename": "ocean_whispers.txt",
            "content": "The blue waves crash\n<<<ERR>>>Salt in the air\nSilence follows the roar.",
            "title": "Ocean Whispers",
            "lines": 3
        },
        {
            "filename": "midnight_ink.tmp",
            "content": "Staring at the blank page\n<<<ERR>>>The moon is my only witness\nWords flow like slow honey\nIn the quiet of the night.",
            "title": "Midnight Ink",
            "lines": 4
        },
        {
            "filename": "cactus_flower.txt",
            "content": "Dry earth beneath me\nThirsting for the rain\nA bloom in the desert\n<<<ERR>>>Against all odds.",
            "title": "Cactus Flower",
            "lines": 4
        }
    ]

    for p in poems:
        with open(os.path.join("drafts", p["filename"]), "w", encoding="utf-8") as f:
            f.write(p["content"])

    # 干扰文件
    with open("drafts/random_notes.log", "w") as f:
        f.write("Buy more pens\nCheck homework deadlines\n<<<ERR>>>")

if __name__ == "__main__":
    build_env()
