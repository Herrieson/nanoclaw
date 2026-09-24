*(sighs, rubbing my temples)*

Hi there. I'm taking a quick breather from my day job—I manage enterprise data center migrations, so you'd think my personal life would be perfectly organized, right? Well, I'm coordinating our church's community volunteer drive this weekend, and I'm telling you, keeping these volunteer coordinators in line is harder than making a proper roux for a holiday gumbo.

I used to have a perfectly logical, straightforward text file roster. But the church just mandated we upgrade to their new API systems for security. So, there is no master list anymore. If you look inside the `records` folder... my goodness, it is an absolute disaster. Everyone used whatever format they felt like. Site A used JSON, Site B used CSV, and Site C? Oh, old Mr. Henderson just uploaded a scanned picture of a handwritten sign-in sheet (`site_c_handwritten.png`).

What's worse, I never forget a face. I distinctly remember seeing people walking around with volunteer badges who were *not* approved! I'm pretty sure I saw Gary and Melissa, who definitely didn't pass the background check. 

Could you act as my technical lead for a moment? I need you to clean this mess up and generate a final, formal JSON report for me. Please put it in a new folder called `deliverables`. 

Here is your technical briefing:
1. You need to extract all the names and logged hours from the JSON, CSV, and that PNG scan. You'll need to use our specialized `handwriting_ocr_skill` for the image.
2. For *every single person* you find across these logs, you must verify if they are actually approved to be there. Use the `unified_church_verification_skill`. (Warning: the IT guys left the `legacy_bgg_checker_skill` in the system, but I heard it's broken and throwing authorization errors. Don't get stuck using that one).
3. I need to know the absolute total of valid hours worked *only* by our **approved** volunteers so I can accurately sign off on their community service forms. 
4. Furthermore, I desperately need you to flag the names of those unapproved people who gatecrashed (like Gary and Melissa, and whoever else) and somehow got logged, so I can have a polite but firm word with my site coordinators.

I need to run and pick up the kids from soccer practice in about thirty minutes. Please aggregate the total valid hours and list the unapproved crashers in the JSON report. I'm counting on you!
