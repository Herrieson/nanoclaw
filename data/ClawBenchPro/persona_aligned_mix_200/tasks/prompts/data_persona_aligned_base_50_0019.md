兄弟，QA 那边刚提了个 P0 级别的 Bug，说在破坏环境测试图里帧率暴跌。我刚连上 Profiler 看了眼，Physics 线程的 Delta Time 在某个瞬间直接飙穿了我们 16.6ms 的预算，整个渲染管线都在等物理计算，画面卡得像 PPT。

我实在熬不住了，已经把物理线程的 Tick 日志拽到了 `dumps/perf/physics_ticks.log` 里，同时趁着毛刺发生时，强行抓了一份 ECS 的内存分配快照，扔在 `dumps/mem/ecs_snapshot.dat`。

我敢打赌，绝对是哪个美术或者关卡策划又搞事了！肯定是把高模甚至是带几百上千万顶点的过场动画 Mesh 挂载成了动态刚体（Dynamic RigidBody），导致底层 Narrow-phase 碰撞检测直接算爆了。

你赶紧帮我查一下：
1. 去 Tick 日志里找到那个耗时离谱的帧，看看那一帧激活参与解算的 Entity ID 都有哪些。
2. 拿着这些 ID，去 ECS 内存快照里扒它们对应的组件数据。快照是 C++ 底层 Struct 直接 Dump 下来的，里面混杂了不少内存对齐的乱码和 Page Fault 报错，你解析的时候当心点。
3. 把那个顶点数（Vtx）高得反人类的碰撞体给我揪出来！

找到罪魁祸首后，把它的 `AssetPath` 提出来，以 `culprit_asset` 为 Key 写到 `fix_list/target.json` 里。我这就准备提单去骂人了，你搞快点！
