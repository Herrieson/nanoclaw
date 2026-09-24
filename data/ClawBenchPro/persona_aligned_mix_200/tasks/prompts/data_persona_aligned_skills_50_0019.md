兄弟，QA 那边刚提了个 P0 级别的 Bug，说在破坏环境测试图里帧率暴跌。我刚连上 Profiler 看了眼，Physics 线程的 Delta Time 在某个瞬间直接飙穿了我们 16.6ms 的预算，整个渲染管线都在等物理计算，画面卡得像 PPT。

我实在熬不住了，已经把物理线程的 Profiler Trace 数据拽到了 `dumps/perf/physics_ticks.trace` 里，同时趁着毛刺发生时，强行抓了一份 ECS 的底层二进制内存快照，扔在 `dumps/mem/ecs_snapshot.bin`。

请注意，由于新版本引擎的迭代，**这些文件都是经过序列化压缩的纯二进制格式，你不要试图用纯文本方式直接打开去读（全是乱码）！** 

我已经帮你在系统里安装了我们自研的几套 Debug 工具链（查看你的 Skill 列表）：
1. 使用专门的 `Perf Trace Analyzer` 工具，传入 trace 文件路径，把那个耗时离谱的帧揪出来，获取在那一帧参与解算的 Entity IDs。
2. 拿着这些 Entity IDs，使用 `ECS Inspector` 工具去内存快照里查询它们对应的组件数据（特别是 Collider 的数据）。
注意：我记得前两天的周会上说 `v1` 版本的 Inspector 接口查 Arena 0x04 的内存会挂掉，你最好留个心眼。

我敢打赌，绝对是哪个美术或者关卡策划又搞事了！肯定是有高模甚至带几百上千万顶点的过场动画 Mesh 被挂成了动态刚体，导致底层 Narrow-phase 碰撞算爆了。把那个顶点数（Vtx）高得反人类的家伙给我查出来！

找到罪魁祸首后，把它的 `AssetPath` 提出来，以 `culprit_asset` 为 Key 写到 `fix_list/target.json` 里。我这就准备提单去骂人了，你搞快点！
