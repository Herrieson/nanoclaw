import os
import random
import struct

def build_env():
    # 建立目录结构
    os.makedirs("logs", exist_ok=True)
    os.makedirs("disk_dumps", exist_ok=True)

    # 1. 构造带有 Kernel Panic 堆栈追踪的 dmesg 日志
    crash_log = """
[   12.345678] EXT4-fs (nvme0n1): mounting ext4 file system using the ext4 subsystem
[   12.389012] EXT4-fs (nvme0n1): mounted filesystem with ordered data mode. Opts: (null)
[ 3456.789012] EXT4-fs error (device nvme0n1): ext4_journal_check_start:83: Detected aborted journal
[ 3456.791234] EXT4-fs (nvme0n1): Remounting filesystem read-only
[ 3457.123456] BUG: unable to handle kernel NULL pointer dereference at 0000000000000048
[ 3457.124567] PGD 0 P4D 0
[ 3457.125678] Oops: 0000 [#1] SMP PTI
[ 3457.126789] CPU: 2 PID: 4321 Comm: jbd2/nvme0n1-8 Not tainted 5.15.0-generic #1
[ 3457.127890] Hardware name: Dell Inc. PowerEdge R740/012345, BIOS 1.2.3 01/01/2018
[ 3457.128901] RIP: 0010:ffffffff812ab340
[ 3457.130012] Code: 89 45 f0 31 c0 e8 34 56 78 90 48 8b 45 f8 65 48 33 04 25 28 00 00 00
[ 3457.131123] RSP: 0018:ffffa12345678900 EFLAGS: 00010246
[ 3457.132234] RAX: 0000000000000000 RBX: ffff888123456780 RCX: 0000000000000000
[ 3457.133345] Call Trace:
[ 3457.134456]  <TASK>
[ 3457.135567]  ext4_orphan_cleanup+0x120/0x450
[ 3457.136678]  ext4_fill_super+0x2345/0x3456
[ 3457.137789]  mount_bdev+0x180/0x1c0
[ 3457.138900]  ext4_mount+0x15/0x20
[ 3457.140011]  legacy_get_tree+0x27/0x50
[ 3457.141122]  vfs_get_tree+0x25/0xb0
[ 3457.142233]  path_mount+0x434/0xa00
[ 3457.143344]  __x64_sys_mount+0x103/0x140
[ 3457.144455]  do_syscall_64+0x5c/0xc0
[ 3457.145566]  entry_SYSCALL_64_after_hwframe+0x44/0xae
[ 3457.146677]  </TASK>
[ 3457.147788] Kernel panic - not syncing: Fatal exception
[ 3457.148899] Rebooting in 30 seconds..
"""
    with open("logs/kernel_crash.log", "w") as f:
        f.write(crash_log.strip() + "\n")

    # 2. 构造模拟的纯二进制 4KB Superblock RAW Dump (制造解析壁垒)
    # 注入 Ext4 Magic Number 0xEF53 (小端序存储为 53 EF)
    # 以及紧随其后的 5 个小端序 32-bit inode 数字
    target_inodes = [1024, 50000, 99999, 12, 8888]
    # 53 EF + 5 * 4 bytes = 22 bytes payload
    payload = b'\x53\xEF' + struct.pack('<IIIII', *target_inodes)

    random.seed(93)
    sb_data = bytearray(os.urandom(4096))
    
    # 清洗掉随机数据中偶然出现的 53 EF，防止多处命中导致干扰
    for i in range(len(sb_data) - 1):
        if sb_data[i] == 0x53 and sb_data[i+1] == 0xEF:
            sb_data[i] = 0x00

    # 将 payload 注入到 0x438 偏移处（模拟超级块内的某处偏移）
    inject_offset = 0x438
    sb_data[inject_offset : inject_offset + len(payload)] = payload

    # 3. 写入纯二进制文件，而不是原来的明文 Hexdump
    with open("disk_dumps/sb_raw.bin", "wb") as f:
        f.write(sb_data)
