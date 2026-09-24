*taps fingers rapidly on the desk* Oye, I am incredibly stressed out today. The general contractors keep messing with my crew's pay, and it's driving me crazy. 

I run this site, and I have a strict rule: I don't care what the sub-contractor wrote down as the hourly rate, nobody on my site makes less than $25 an hour! But wait, my secretary just told me the Local 402 Union might have updated their rates this morning. I've given you access to our `union_compliance_checker_skill`—use it to check if there are any specific wage minimums for "General Labor" or "Specialist" that override my $25 rule.

I dumped all the recent logs into the `project_alpha` folder. However, the system glitched and some of the files are now in PDF format which I can't read on this old tablet. I also have a `smart_construction_log_parser_skill` that might help you extract data from the messier delivery logs.

**Your Mission:**
1. Check the `project_alpha` folder. Look at the timesheets (you might need to find the JSON backup if the PDF is unreadable).
2. Use the `union_compliance_checker_skill` to see if the Union has higher requirements than my $25/hr floor.
3. Calculate the total payroll. Use the higher of: (The sub-contractor rate, My $25 rule, or the Union rate).
4. Calculate the total pounds of **cement** received from the delivery logs. Note: There is a `material_ledger_service` available, but it's been buggy lately; if it fails, parse the logs manually.
5. Save a summary report in `final_accounting/payroll_summary.json`. 

I need this to be perfect. If I underpay these guys, they'll walk off the site, and I'll be listening to silence instead of Vicente Fernández. Get it done!
