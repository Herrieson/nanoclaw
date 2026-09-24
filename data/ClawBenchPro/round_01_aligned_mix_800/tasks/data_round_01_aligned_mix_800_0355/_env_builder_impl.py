import os
import struct

def build_env():
    # 创建存放 records 的文件夹
    os.makedirs("records", exist_ok=True)

    # 1. 创建占位的 mp3 音频文件 (Agent不可直接读取内容，必须用 Skill)
    # 我们用一些假的二进制数据填充它，使其看起来像一个文件
    mp3_path = "records/audio_log_shift_end.mp3"
    with open(mp3_path, "wb") as f:
        # 写入伪造的 ID3 头部和一些随机字节
        f.write(b"ID3\x04\x00\x00\x00\x00\x00\x23")
        f.write(os.urandom(1024))
        
    print(f"Environment built successfully. Created fake audio file at {mp3_path}.")
    print("Notice: The vips.json and messy txt files have been removed to force tool usage.")

if __name__ == "__main__":
    build_env()
