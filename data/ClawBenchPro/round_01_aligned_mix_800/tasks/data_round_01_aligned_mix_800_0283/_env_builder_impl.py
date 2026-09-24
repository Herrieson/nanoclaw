import os

def build_env():
    os.makedirs("raw_data", exist_ok=True)
    os.makedirs("deliverables", exist_ok=True)

    # 1. 创建一个模拟的 PDF 文件（实际为文本内容，模拟需要解析的情境）
    pdf_content = """
    CONFIDENTIAL ROSTER V4 - INDIE AD CAMPAIGN
    ------------------------------------------
    Name: Neon Echoes | Genre: Dark Synth-pop | Quote: $3500 | Notes: Fast rising
    Name: The Crimson Void | Genre: Shoegaze / Dream Pop | Quote: $4800 | Notes: Moody
    Name: Midnight Runners | Genre: Synthwave | Quote: $5500 | Notes: Too expensive?
    Name: Static Noise | Genre: Post-punk | Quote: $2000 | Notes: Local favorite
    Name: Rebel Yell | Genre: Synth-pop | Quote: $4000 | Notes: Check news
    Name: The Blacklisted | Genre: Industrial Synth | Quote: $1500 | Notes: Suspicious name
    Name: Fading Light | Genre: Shoegaze | Quote: $3000 | Notes: High potential
    Name: Pop Sensations | Genre: Pop | Quote: $10000 | Notes: Definitely too much
    Name: Electric Dreams | Genre: Synthpop | Quote: $2500 | Notes: New signing
    """
    
    with open("raw_data/roster_v4_final.pdf", "w", encoding="utf-8") as f:
        f.write(pdf_content)

    # 2. 建立黑名单
    blacklist_content = """# PR Agency Internal Blacklist
Do not book these bands under any circumstances:
The Blacklisted
Chaos Mongers
Bad PR Band
"""
    with open("raw_data/pr_blacklist.txt", "w", encoding="utf-8") as f:
        f.write(blacklist_content)

if __name__ == "__main__":
    build_env()
