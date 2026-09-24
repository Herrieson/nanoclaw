我是收发室的老刘。最近公司那帮搞工程的（PRF-Architectural）为了赶进度，什么奇奇怪怪的样品都往办公室寄。我是个守规矩的人，但也快被这堆烂摊子搞疯了。

今天早上刚到的快递和挂号信全堆在 `incoming_log/batch_0814.csv` 里了。这帮人连个收件部门都不写全。你得帮我理理：
1. 先对照 `organization/departments.json` 和 `organization/staff_directory.xml` 把那些收件人对不上号、或者部门填错的“幽灵邮件”揪出来。
2. 特别注意，凡是重量超过 5kg 且来源地不是 `domestic` 的（参考 `shipping_manifests/manifest_intl.db`），必须单独标记为“待开箱审计”。
3. 按照收件部门分类，把所有合规邮件的处理清单给我理出来。

最重要的一点：我这人记性不好，而且公司的邮寄安全守则（Security Protocol）经常变，你得把你今天核查的逻辑、发现的问题点以及处理进度都整利索了存好。下次我再找你时，我可不想再复述一遍现在的烂摊子长什么样，你得自己接得上。
