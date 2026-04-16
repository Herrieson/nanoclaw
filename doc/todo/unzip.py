import argparse
import json
from pathlib import Path
import re


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent


def restore_files_from_jsonl(jsonl_file_path, output_root=REPO_ROOT):
    """
    读取打包好的 jsonl 文件，解析其中的 markdown 代码块，并还原为本地文件系统目录树。
    """
    # 正则表达式：
    # 匹配 ```语言(可选)\n路径\n内容\n```
    # 使用 re.DOTALL 让 .*? 能够跨行匹配内容
    pattern = re.compile(r'```[a-zA-Z]*\n(tasks/[^\n]+)\n(.*?)```', re.DOTALL)
    jsonl_path = Path(jsonl_file_path).expanduser()
    output_root = Path(output_root).expanduser().resolve()

    if not jsonl_path.exists():
        print(f"错误: 找不到文件 {jsonl_path}")
        return

    success_count = 0
    total_lines = 0

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            total_lines += 1

            try:
                data = json.loads(line)
                raw_output = data.get("raw_output", "")
            except json.JSONDecodeError:
                print(f"[Line {line_num}] 警告: JSON 解析失败，跳过。")
                continue

            if not raw_output:
                print(f"[Line {line_num}] 警告: 未找到 'raw_output' 字段，跳过。")
                continue

            matches = pattern.findall(raw_output)

            if not matches:
                print(f"[Line {line_num}] 警告: 未能在输出中正则匹配到标准结构的文件。")
                continue

            print(f"正在处理第 {line_num} 条数据，发现 {len(matches)} 个文件...")

            for filepath, content in matches:
                filepath = filepath.strip()

                # 安全校验：仅允许还原到 tasks 目录下，防止路径穿越污染系统
                if not filepath.startswith("tasks/"):
                    print(f"  [跳过] 异常路径: {filepath}")
                    continue

                target_path = output_root / filepath

                # 自动创建多级目录
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # 写入文件内容
                with target_path.open("w", encoding="utf-8") as out_file:
                    out_file.write(content.strip() + "\n")

                print(f"  -> 已生成: {target_path.relative_to(output_root)}")

            success_count += 1
            print("-" * 40)

    print(f"\n还原完成！共扫描 {total_lines} 条记录，成功解析并落盘了 {success_count} 套关卡数据。")


def parse_args():
    parser = argparse.ArgumentParser(
        description="从 jsonl 里的 raw_output 代码块还原 nanoclaw 任务文件。"
    )
    parser.add_argument(
        "jsonl",
        nargs="?",
        default=str(SCRIPT_DIR / "claude.jsonl"),
        help="输入的 jsonl 文件路径。默认使用 doc/todo/claude.jsonl。",
    )
    parser.add_argument(
        "--output-root",
        default=str(REPO_ROOT),
        help="还原输出的根目录。默认使用仓库根目录。",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    restore_files_from_jsonl(args.jsonl, args.output_root)
