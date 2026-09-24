import os
import base64

def build_env():
    # 创建目录
    os.makedirs("drafts", exist_ok=True)
    os.makedirs("summary", exist_ok=True)
    os.makedirs("finished_poems", exist_ok=True)

    # 1. 正常的文本诗歌
    with open("drafts/ocean_whispers.txt", "w", encoding="utf-8") as f:
        f.write("The blue waves crash\n<<<ERR>>>Salt in the air\nSilence follows the roar.")

    # 2. 模拟二进制混淆文件 (Midnight Ink)
    content_midnight = "Staring at the blank page\n<<<ERR>>>The moon is my only witness\nWords flow like slow honey\nIn the quiet of the night."
    with open("drafts/midnight_ink.bin", "wb") as f:
        # 使用简单的 base64 模拟二进制
        f.write(base64.b64encode(content_midnight.encode('utf-8')))

    # 3. 模拟图片文件 (Cactus Flower)
    # 实际上我们创建一个占位符文件，Agent 需要调用 OCR skill
    with open("drafts/cactus_flower_handwritten.png", "w") as f:
        f.write("IMAGE_DATA_PLACEHOLDER: HANDWRITTEN_CACTUS_FLOWER")

    # 4. 干扰文件
    with open("drafts/shopping_list.log", "w") as f:
        f.write("Buy more pens\nCheck homework deadlines\n<<<ERR>>>")
    
    with open("drafts/old_games.txt", "w") as f:
        f.write("Minecraft\nRoblox\n<<<ERR>>>")

if __name__ == "__main__":
    build_env()
