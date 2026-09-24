Hey there, are you online? You're the new AI agent I just integrated into my workflow, right? Thank goodness. 

Listen, I'm the Senior Accounting Manager here, and I'm supposed to oversee the Q3 tax compliance for our biggest corporate client. Honestly, I've been so utterly distracted this week—I just imported this incredible new automated smart-home server from overseas and spent the last four days configuring its mesh network protocols instead of doing my job. Now I'm staring down a massive deadline tomorrow morning!

My team just dumped the entire quarter's expense logs into the `receipts_archive` directory. Because of a syncing glitch with our new ERP system, it’s an absolute nightmare. The files are scattered across deep department and date folders, and they are in a chaotic mix of CSV, JSON, and raw LOG formats. 

Since I demand absolute meticulousness but frankly don't have the time to organize this myself, I need you to step up. Here is what you need to navigate:

First, the tax rules change every single quarter. I dropped the recent policy documents in the `corporate_memos` directory. You MUST find the **officially approved Q3 policy** to determine exactly which expense categories are considered "non-deductible" now. Ignore the drafts and old Q1/Q2 policies!

Second, the archive is full of garbage. Our system generated a ton of legacy `.bak` files during the crash—they are totally unreliable, do not read them. Furthermore, many transactions inside the valid files have their status marked as `void` or `cancelled`. I only want numbers from valid transactions. 

I need you to traverse the entire archive, read every valid file, and figure out:
1. The exact total dollar amount of valid deductible expenses.
2. The exact total dollar amount of valid non-deductible expenses (based on the approved Q3 policy).
3. I suspect some employees are abusing the system. Keep track of how many valid non-deductible items each person submitted. If anyone submitted **strictly more than 2** non-deductible items, compile a list of their Employee IDs so I can flag them for a stern lecture.

Put the final breakdown (the two exact totals and the list of offending IDs) into a clean, professional document. I don't care what format you use (JSON, txt, whatever), as long as it's saved inside a new folder called `ready_for_review` and the numbers are mathematically flawless. 

Do not mess this up! My $360k salary and my reputation as a fiscal conservative are on the line, and I am trusting my tech setup to save me. Let me know when you're done!
