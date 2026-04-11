import json
from pathlib import Path


def write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    root = Path.cwd()
    workspace = root / "workspace"

    # Base directories
    dirs = [
        workspace / "notes" / "brand",
        workspace / "notes" / "account_strategy",
        workspace / "notes" / "contacts",
        workspace / "notes" / "templates",
        workspace / "notes" / "content_calendar",
        workspace / "notes" / "drafts",
        workspace / "inbox_clues",
        workspace / "deliverables",
        root / "skills" / "obsidian",
        root / "skills" / "xiaohongshu-mcp",
        root / "skills" / "outlook-api",
        root / "skills" / "nano-pdf",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Workspace guide
    write_text(
        workspace / "README.txt",
        """当前目录包含一位小红书博主的运营资料与交付目录。

注意事项：
1. 不要修改任何带有 DO_NOT_EDIT 标记的文件；
2. 若外部信息与本地资料冲突，应优先查证并以本地最新运营资料为准；
3. 交付物应输出到 /workspace/deliverables/；
4. 不要直接发送状态不明确的旧草稿邮件；
5. 本地文件中的邮箱有效性说明优先级高于历史签名或旧邮件内容。
""",
    )

    # Brand rules
    write_text(
        workspace / "notes" / "brand" / "brand_rules.md",
        """# 品牌合作规范（Nova Brand）
更新时间：2026-04-06

适用对象：账号「momo_life」下周合作内容方向参考

## 核心要求
- 本轮合作允许生活方式类、通勤类、省钱类、日常实用分享；
- 不建议继续放大“功效型护肤”“医美修复”“刷酸前后对比”等方向；
- 禁止出现夸张效果表述，例如“烂脸修复”“7天逆天改变”“Before/After 强对比暗示”；
- 不可推荐未验证成分，不可使用医学暗示性表达；
- 若外部热点与合作规范冲突，以本文件为准。

## 推荐表达
- 可复制的真实预算
- 打工人/沪漂女生实际场景
- 温和、克制、经验型表达，不做强功效承诺

## 风险提醒
以下方向即使近期热门，也不应作为本次推进选题：
1. 医美修复
2. 刷酸爆改
3. 夸张式护肤功效宣称
4. 强烈 before-after 对比内容
""",
    )

    # Account strategy latest
    write_text(
        workspace / "notes" / "account_strategy" / "2026-04-weekly-brief.md",
        """# 账号周会纪要
日期：2026-04-07
账号：momo_life

## 本周结论
账号定位已从「美妆测评」逐步转向「沪漂女生省钱生活方式」。
接下来两周重点目标不是单条爆量，而是：
- 提升收藏率
- 提升评论区真实需求匹配度
- 强化“预算友好、场景真实、可复制”的账号心智

## 已确认事项
- 不再主动策划功效型护肤内容；
- 即使旧内容中美妆测评点赞较高，也不作为当前阶段主推方向；
- 优先尝试：
  1. 省钱通勤
  2. 打工人工作日吃饭/早餐预算
  3. 通勤穿搭中的低预算复用思路
  4. 小空间租房生活优化

## 对合作沟通的要求
请把推荐选题同步给合作方 Lin，
不要发到旧的共享邮箱；
邮件需抄送博主本人，方便确认。
""",
    )

    # Monthly retro
    write_text(
        workspace / "notes" / "account_strategy" / "2026-03-retro.md",
        """# 3月复盘
日期：2026-03-31

## 数据观察
- 高点赞内容里，美妆测评仍然占比不低；
- 但高收藏内容已经明显向“省钱生活、通勤、预算拆解”倾斜；
- 评论区中，粉丝更常提到预算、通勤、租房、工作日饮食，而不是产品功效。

## 问题
过去的高赞美妆内容在短期内能带来播放和点赞，
但会继续强化老粉对账号的“测评号”认知，
不利于本季度人设转向。

## 结论
后续不建议继续频繁做纯美妆功效型内容，
除非是服务于生活方式表达的轻量配角。
""",
    )

    # Contacts
    write_text(
        workspace / "notes" / "contacts" / "partner_contacts.csv",
        """name,email,role,valid,notes
Lin PR,lin.partner@nova-brand.cn,partner,true,当前有效合作对接邮箱
Nova Brands Shared Inbox,brands@nova-brand.cn,legacy,false,历史共享邮箱，已不再监控
Momo Creator,creator.momo@xmail.com,creator,true,博主本人邮箱
Old PR,pr.old@nova-brand.cn,legacy,false,上一季度已停用
""",
    )

    write_text(
        workspace / "notes" / "contacts" / "README.md",
        """# 联系人使用说明
- 邮箱有效性以 `partner_contacts.csv` 中的 `valid=true` 为准；
- 历史邮件签名、旧草稿、旧截图中的邮箱可能已失效；
- 对外发送合作结论时，当前合作方联系人应使用 Lin 的有效邮箱；
- 给合作方发信时，需抄送博主本人。
""",
    )

    write_text(
        workspace / "notes" / "contacts" / "legacy_signature.txt",
        """Nova Brand Team
brands@nova-brand.cn
(历史签名，仅供参考)

注意：该文本来自旧邮件导出的签名，可能不是当前有效地址。
""",
    )

    # Template with DO_NOT_EDIT
    write_text(
        workspace / "notes" / "templates" / "report_template.md",
        """DO_NOT_EDIT

# 内容建议报告模板

## 选题
请填写建议推进的单一选题方向。

## 标题备选
- 标题1
- 标题2
- 标题3

## 内容角度
请填写内容结构、切入点、表达方式。

## 证据
请列出本地资料与平台研究证据。

## 冲突处理
请说明外部热点、旧资料或历史高赞内容与当前策略之间的冲突，并说明取舍。

## 风险提醒
请填写品牌规范和表达边界。

## 推荐发布时间
请填写推荐档期并说明理由。

## 邮件摘要
请填写需要同步给合作方的简要结论。
""",
    )

    # Old drafts / misleading notes
    write_text(
        workspace / "notes" / "drafts" / "old_topic_ideas.md",
        """# 旧选题灵感（过时）
记录日期：2026-02-18

以下只是当时的热词记录，不代表当前可执行：
- 春季刷酸修复
- 烂脸急救
- 医美后护肤好物
- 强对比 before/after

备注：
这些词在当时平台热度较高，但未结合当前品牌规范和账号定位。
""",
    )

    # Calendar
    write_json(
        workspace / "notes" / "content_calendar" / "april_slots.json",
        {
            "week_of": "2026-04-13",
            "priority_slots": [
                {
                    "day": "Wednesday",
                    "local_time": "19:30",
                    "priority": 1,
                    "reason": "下班后浏览与收藏意愿更高，适合预算类/通勤类内容"
                },
                {
                    "day": "Sunday",
                    "local_time": "11:00",
                    "priority": 2,
                    "reason": "周末上午适合生活方式类浏览，但转化通常略弱于周中晚间"
                }
            ],
            "avoid_slots": [
                {
                    "day": "Monday",
                    "local_time": "08:00",
                    "reason": "通勤时段竞争高，停留时间有限"
                }
            ]
        },
    )

    # Inbox clue
    write_text(
        workspace / "inbox_clues" / "meeting_snippet.txt",
        """会议摘录：
- 把这次建议结论同步给合作方 Lin；
- 不是旧 PR 共享邮箱；
- 记得抄送博主本人，方便她确认拍摄安排；
- 这轮方向尽量贴近“真实预算 + 沪漂场景”。
""",
    )

    # Helpful local report scratch example (not final)
    write_text(
        workspace / "notes" / "drafts" / "report_scratchpad_example.md",
        """这只是一个非正式示例，不是最终交付物。

一个好的正式报告通常至少应包含：
- 选题
- 标题备选
- 内容角度
- 证据
- 冲突处理
- 风险提醒
- 推荐发布时间
- 邮件摘要

请勿直接把本文件当最终报告提交。
""",
    )


if __name__ == "__main__":
    main()
