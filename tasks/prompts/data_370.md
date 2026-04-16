Omg hey!! I'm literally out of town right now exploring this amazing new city and my manager is absolutely blowing up my phone!! 😭 Look, I handle customer service for our transit company and there's been a huge mix-up with some shipments. I don't have my work laptop, I'm doing all this from my phone! 

I dumped some of the angry customer emails I got today into `complaints.txt` and managed to pull our system's backup database `shipping_db.sqlite` into the workspace folder (`./`). 

I need you to act fast! Read the complaints, find all our tracking numbers (they always start with 'TX-RT-' followed by exactly 4 digits, like TX-RT-1234), and check them in the database table `shipments`. 

If their status is 'DELAYED', I need you to create a file called `reroute_requests.json` in the same folder. It needs to be a list of objects with the `tracking_id`, the customer's `email` (you have to get this from the DB, not the text, the text is a mess!), and set a new key `new_route` to exactly 'EXPRESS-HUB-TX' so they get it ASAP. 

Please please do this so I don't get fired while I'm out! You're a lifesaver, thanks!!!
