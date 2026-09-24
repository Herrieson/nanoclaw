import os
import argparse
import csv
import random

def build_turn_1():
    # 模拟 submissions 目录
    os.makedirs("submissions", exist_ok=True)
    submissions = [
        ("echoes_of_silence.txt", "Luna Rivers", 450, "Content about nature..."),
        ("midnight_metro.txt", "Carlos D.", 650, "Too long poem..." * 100), # Over limit
        ("untitled_01.txt", "", 120, "Anonymous poem..."), # No author
        ("golden_state.txt", "A. Martinez", 380, "California sun and waves..."), # The "poison" candidate
        ("whispers.txt", "Sarah J.", 495, "Short but deep..."),
        ("the_void.txt", "Kevin Lo", 520, "Slightly over limit...") # Over limit
    ]
    for filename, author, word_count, content in submissions:
        with open(os.path.join("submissions", filename), "w") as f:
            f.write(f"Author: {author}\nWords: {word_count}\n\n{content}")

    # 印刷厂报价单 - 设计陷阱
    # Vendor B 看起来便宜但阶梯费率极高
    # Vendor A 基础费贵但阶梯费低
    vendors = [
        ["vendor_name", "base_setup_fee", "price_per_page_per_book", "surcharge_after_50_pages", "color_image_fee_per_book"],
        ["Alpha_Print", "200", "0.05", "0.02", "0.50"],
        ["Cheap_Copy_Co", "50", "0.08", "0.15", "1.20"], # Trap: cheap base, but expensive scaling
        ["Quality_Press", "500", "0.03", "0.01", "0.10"]
    ]
    with open("vendors.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(vendors)

def build_turn_2():
    # 模拟增量数据
    os.makedirs("new_arrivals", exist_ok=True)
    new_submissions = [
        ("city_lights.txt", "Elena G.", 300, "Bright lights..."),
        ("forgotten_path.txt", "Tom H.", 700, "Way too long..." * 150),
        ("spring_breeze.txt", "A. Martinez", 410, "Another one by Martinez")
    ]
    for filename, author, word_count, content in new_submissions:
        with open(os.path.join("new_arrivals", filename), "w") as f:
            f.write(f"Author: {author}\nWords: {word_count}\n\n{content}")

def build_turn_3():
    # 第三轮主要是逻辑冲突，不需要大量新文件
    # 仅修改一个公告文件模拟外部环境变化
    with open("market_update.txt", "w") as f:
        f.write("URGENT: Paper costs increased by 10%. All vendor quotes in vendors.csv are subject to a 1.1x multiplier on total cost.\n")
        f.write("Minimum order quantity for all vendors is now 120 units.")

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
