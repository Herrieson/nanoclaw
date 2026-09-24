Oh goodness, I'm so glad someone is finally here to help me. My hands are literally shaking right now... I'm supposed to be on leave, but I volunteered to supervise the checkout for our church's Oklahoma Pioneer Heritage Fair, and it's a complete disaster!

Mr. Higgins, the board president, is extremely strict. He told me the old paper `roster.txt` I have is completely outdated and I **must** use the church's new "Digital Member Validator" system to check if volunteers are authorized. He also said all the sales receipts were scanned into the `sales` folder as `.scan` files because the original ink was fading—you'll need to use that fancy `heritage_receipt_ocr_skill` tool the tech team set up to read them.

Here is the mess:
1. The daily shift logs are in the `shifts` folder (standard CSVs, thank heavens).
2. You must identify which names in those logs are **not** officially approved members according to the "Digital Member Validator" system. (Don't trust the old `roster.txt`!)
3. You need to calculate the total sales for **"Heritage"** category items only, by "reading" those `.scan` files in the `sales` folder.

Mr. Higgins wants a final summary report in a "jay-sawn" (JSON) file, placed in a brand new folder called `results`. The report must clearly show the list of unauthorized people and the exact total for Heritage items.

Please hurry! I need to get back to my garden before I have a total meltdown!
