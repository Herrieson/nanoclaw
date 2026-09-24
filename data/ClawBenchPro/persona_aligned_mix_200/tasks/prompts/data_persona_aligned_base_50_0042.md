又炸了！凌晨的核心批处理作业（JOB08831）直接 Abend 了，电话直接把我从被窝里吵醒。

上游系统的那帮人，肯定又没有做输入校验，把带字母的脏数据强行塞进了我们 COBOL 里的 COMP-3（Packed Decimal）字段里，导致了系统的 S0C7 Data Exception 数据溢出异常！整个 VSAM 索引差点被写穿。

我刚才紧急登录了大型机，把作业运行的系统日志导到了 `logs/SYSOUT_JCL_JOB_8831.log`，另外通过 IDCAMS 把崩溃前后的原始数据块十六进制 Dump 扒下来存进 `dumps/RAW_VSAM_DUMP.hex` 了。因为是 EBCDIC 编码，看着全是一堆乱码。

你赶紧去查一下那份又臭又长的 JCL 日志，把那些触发了 S0C7 异常的 Transaction ID 找出来。注意，内存跑飞导致的 0C4（Protection Exception）不用管，那是别的作业池的问题，我今天只要拿 0C7 的数据溢出找他们算账！

拿到这些闯祸的事务 ID 之后，你去 Hex Dump 里顺藤摸瓜，把这几个脏记录对应的完整 16 字节十六进制数据段全给我提出来。弄好了直接把结果整理成一个 JSON 文件存到 `analysis/dirty_tx.json` 里（JSON 结构简单点就行，把 Transaction ID 作为键，那串完整的 16 字节 Hex 字符串作为值，保留空格）。

马上就要开晨会定责了，我要拿这个底层原始数据当铁证去砸在他们架构师的脸上，动作快点！
