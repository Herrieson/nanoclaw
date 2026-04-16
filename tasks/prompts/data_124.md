Hey there! Hola! Man, it has been an absolutely crazy week. The kids (both of 'em!) are running wild around the house, and I'm right in the middle of slow-cooking some traditional kanuchi for dinner. I really can't deal with work stuff right now, but I have a deadline. 

I run my own testing and inspection gig for medical gear—mostly pulse oximeters and infusion pumps. I do a good job, but honestly, my record-keeping is a complete disaster. I just dump all my notes, CSVs, and text files into a folder. To make matters worse, my eyes have been giving me a lot of trouble lately, and staring at these tiny fonts on the terminal is just killing me. 

Everything is in my workspace folder. There's a `manual.txt` where I scribbled down the failure thresholds for the different devices, and a `records` folder with all my messy testing logs from this week. 

I need you to dig through that `records` folder, figure out which devices failed the QA check based on the rules in `manual.txt`, and generate a clean `failed_devices.json` file right in the main workspace directory. The JSON should just be a list of dictionaries, like `[{"id": "DEVICE_ID", "reason": "why it failed"}]`. 

I'm gonna go check on the soup. Thanks a million for doing this, you're a lifesaver!
