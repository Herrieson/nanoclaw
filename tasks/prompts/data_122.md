Listen to me carefully, I do not have the time or the patience to explain this twice. My head is already pounding trying to make sense of this mess, and the corporate auditors are breathing down my neck. 

I run a tight ship at this pharmacy. Everything must be perfectly organized, but someone completely screwed up the Schedule II drug intake last Tuesday (2023-10-10). The vault numbers are off, and I will absolutely not take the fall for someone else's incompetence. 

I dumped the raw system files into the current folder. You will find the delivery logs (`deliveries.json`), the vault counts from Monday and Wednesday (`vault_counts.json`), and the employee punch cards (`punch_cards.csv`). 

Here is exactly what you are going to do:
1. Figure out exactly which items are short and by how much based on the deliveries and the vault counts.
2. Cross-reference the exact delivery timestamp of the missing items with the punch cards to figure out who was on duty and signed for it.
3. Generate a strict, perfectly formatted CSV file named `missing_report.csv` with the headers: `Item`, `Expected`, `Actual`, `Discrepancy`.
4. Draft a formal, highly disciplinary warning memo in a file called `memo.txt` addressed to the responsible employee. Do not sugarcoat it. 

I expect this done meticulously. Do not ask me for help, just leave the two files in the directory when you are finished so I can review them and fire whoever did this.
