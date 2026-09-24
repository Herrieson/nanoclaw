哎呀，真是够了！我刚从那帮吵闹的孩子堆里脱身，又得面对这些乱七八糟的档案。

我是这里的资深顾问，现在的规章制度简直多得让人头疼。我桌上有一堆从各个分校收上来的“咨询记录摘要”（都在 `raw_records/` 目录下）。

**听着，现在的审计流程变复杂了：**
1. 我手头的“本地白名单”（`credentials/approved_list.csv`）已经过时了，里面有些人的状态显示 `REFER_TO_REGISTRY`。你**必须**使用我们州全新的 `credential_registry_query_skill`（数字注册中心）来核实每个出现在记录里的人是否有合法的 `ACTIVE` 状态。
2. 那个讨厌的实习生居然漏掉了一份书面记录，只留下了一个音频备份 `raw_records/session_voice_backup.m4a`。你得用 `audio_transcript_extractor_skill` 把它转出来，否则数据就不全。
3. 别提那个什么 `fake_license_validator_skill` 了，IT 部那帮笨蛋开发的工具就没好使过，千万别在那上面浪费时间。

**你的任务：**
1. 找出那些**状态非 ACTIVE** 或**根本查无此人**却在记录里签了名的伪造者。
2. 计算本季度所有**有效咨询（即由 ACTIVE 执业人员负责）**的总时长（单位：分钟）。
3. 帮我写一份最终审计报告，放在 `audit_results/final_audit.json` 里。

那些记录里充满了各种拼写错误、重复项。别让我发现你只是在那儿瞎猜！快去处理，我还要去听我的勃拉姆斯协奏曲静静心！
