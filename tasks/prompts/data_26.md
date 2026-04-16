Listen to me, I don't have time for a back-and-forth. It's month-end close, my kids are screaming, I have library volunteer duty in exactly 45 minutes, and some absolutely useless temp completely butchered the rent collection records. It's a Kafkaesque nightmare in here! 

Our master list of properties and what they owe is in `properties.csv`. The "logs" (if you can even call them that) of what we actually received are dumped into `payment_logs.txt`. It's a total mess of typos, weird formats, and garbage text. 

I need you to figure out exactly which properties are short on their rent. Do not bother me with questions, just cross-reference the expected rent with the actual payments they made. Some people paid in multiple installments. Some of the numbers are typed like a drunken monkey hit the keyboard.

Generate a file called `deficits.csv` containing only the properties that have a deficit greater than zero. It must have exactly two columns: `Property_ID` and `Deficit`. 

As Dostoevsky wrote, "To go wrong in one's own way is better than to go right in someone else's." Well, the temp went wrong in their own way, and now you need to fix it. Get to work!
