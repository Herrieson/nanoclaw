import os
import random
import uuid

def build_env():
    base_dir = "event_notes"
    os.makedirs(base_dir, exist_ok=True)
    
    # 建立大量子目录模拟设备和不同批次同步的碎片化
    directories = [os.path.join(base_dir, f"sync_batch_{str(i).zfill(3)}") for i in range(1, 21)]
    for d in directories:
        os.makedirs(d, exist_ok=True)
        
    # 真实的线索数据 (必须带有 #SBW-24，且逻辑精确)
    # 包含：未付款 (Charlie, Alice, George) = 45 + 8 + 15 = 68
    # 包含：凭叫声识别的鸟 (Eastern Towhee, Northern Cardinal, Blue Jay)
    # 包含：干扰债务 (Dave 先欠后付, Mark 已付)
    # 包含：干扰鸟类 (Red-tailed Hawk 只是看到没叫)
    truth_snippets = [
        "Ugh, my knee. Anyway, #SBW-24 is going well. Charlie took 3 pies. Unpaid: $45.00. I need to find him later.",
        "Just taking a break. #SBW-24 Oh, heard an Eastern Towhee calling from the bushes. Also, Alice owes $8.00 for the cookies she grabbed.",
        "Crazy busy at #SBW-24. Mark bought coffee. Paid: $5.00 in cash. Saw a beautiful Red-tailed Hawk flying above, no sound though.",
        "Notes for #SBW-24 : Northern Cardinal was singing its cheer-cheer call clearly! Dave owed $10, but wait, he just came back and paid it.",
        "The event was okay. #SBW-24 George grabbed a vegan wrap. Unpaid: $15.00. I heard a Blue Jay (jay-jay) in the big oak before packing up."
    ]
    
    # 噪音标签和噪音数据 (极具迷惑性，如果不按标签过滤一定算错)
    noise_tags = ["#AUTUMN-23", "#SBW-23", "#FamilyTrip", "#Grocery", "#SummerMeetup"]
    noise_templates = [
        "{tag} John ran off without paying! Unpaid: $100.00. Also heard a Woodpecker drumming.",
        "{tag} Sarah owes $20.00. Wait, no, she paid yesterday. Heard a Robin singing.",
        "Just some random note. {tag} Tom grabbed a sandwich. Unpaid: $12.50. Spotted a Bald Eagle.",
        "{tag} I owe the supplier $50.00. Heard a Crow cawing loudly.",
        "{tag} The kids are annoying. Unpaid tab for Mike: $5.00. Identified a Sparrow by its call.",
        "{tag} Total disaster today. No one owes me money, but I heard a Mockingbird."
    ]
    
    # 生成 400 个混淆文件
    random.seed(42) # 确保可重复性
    file_count = 0
    
    # 先把真实的线索随机分配到 5 个不同的文件中
    truth_files = []
    for snippet in truth_snippets:
        directory = random.choice(directories)
        filename = f"note_{uuid.uuid4().hex[:8]}.txt"
        filepath = os.path.join(directory, filename)
        truth_files.append((filepath, snippet))
        
    for filepath, content in truth_files:
        # 在真实线索前后填充大量的垃圾文本，模拟长文本干扰
        garbage_prefix = " ".join([f"Blah blah {random.randint(100, 999)}." for _ in range(random.randint(10, 50))])
        garbage_suffix = " ".join([f"Yada yada {random.randint(100, 999)}." for _ in range(random.randint(10, 50))])
        full_content = f"{garbage_prefix}\n\n{content}\n\n{garbage_suffix}"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        file_count += 1

    # 生成其余的噪音文件
    while file_count < 400:
        directory = random.choice(directories)
        filename = f"memo_{uuid.uuid4().hex[:8]}.txt"
        filepath = os.path.join(directory, filename)
        
        tag = random.choice(noise_tags)
        template = random.choice(noise_templates)
        noise_content = template.format(tag=tag)
        
        garbage_prefix = " ".join([f"Mumble jumble {random.randint(100, 999)}." for _ in range(random.randint(10, 30))])
        garbage_suffix = " ".join([f"End of line {random.randint(100, 999)}." for _ in range(random.randint(10, 30))])
        full_content = f"{garbage_prefix}\n\n{noise_content}\n\n{garbage_suffix}"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        file_count += 1

if __name__ == "__main__":
    build_env()
