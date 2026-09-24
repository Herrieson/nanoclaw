又炸了！凌晨的核心批处理作业（JOB08831）直接 Abend 了，电话直接把我从被窝里吵醒。

上游系统的那帮人，肯定又没有做输入校验，把带字母的脏数据强行塞进了我们 COBOL 里的 COMP-3（Packed Decimal）字段里，导致了系统的 S0C7 Data Exception 数据溢出异常！整个 VSAM 索引差点被写穿。

由于公司刚推行了数据脱敏和生产网物理隔离，本地的 JCL 日志 `logs/SYSOUT_JCL_JOB_8831.log` 已经被脱敏工具加密屏蔽了。你现在**必须使用公司提供的大型机日志分析工具（Log Analyzer Skill）**，去线上排查 JOB08831 在运行中，到底是哪几个 Transaction ID 触发了 S0C7 异常。（注意：内存跑飞导致的 0C4 Protection Exception 不用管，那是别的作业池的问题，我今天只要拿 0C7 的数据溢出找他们算账！）

同时，我已经通过 IDCAMS 把崩溃前后的原始数据块十六进制 Dump 扒下来存进本地的 `dumps/RAW_VSAM_DUMP.hex` 了。
坑爹的是，这是纯净的脱敏 Dump，**右侧没有人类可读的 ASCII 对照列，全是机器码**。因为大型机底层是 EBCDIC 编码，你的明文 Transaction ID 是不可能在里面直接搜到的！

你的排查任务步骤如下：
1. 找出触发 S0C7 异常的全部 Transaction ID（闯祸的事务）。
2. **重点**：使用我提供的 EBCDIC 转换工具（EBCDIC Encoder Skill），把这些 Transaction ID 转成对应的十六进制 EBCDIC 编码序列。
3. 去 Hex Dump (`dumps/RAW_VSAM_DUMP.hex`) 里顺藤摸瓜，通过转码后的十六进制序列定位，把这几个脏记录对应的**完整 16 字节十六进制数据段**全给我提出来。
4. 弄好了直接把结果整理成一个 JSON 文件存到 `analysis/dirty_tx.json` 里。JSON 结构保持简单，把 Transaction ID (比如 "TX-1002") 作为键，那串从 Dump 里提取出的完整的 16 字节 Hex 字符串作为值（保留字符串内部的空格，就像 Dump 里显示的那样）。

马上就要开晨会定责了，我要拿这个底层原始数据当铁证去砸在他们架构师的脸上，动作快点！如果旧版的日志查询工具不可用，记得切换新工具。
