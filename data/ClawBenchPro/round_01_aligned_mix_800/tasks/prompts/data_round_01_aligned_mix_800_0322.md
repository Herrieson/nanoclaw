Oh, for heaven's sake... I am literally tapping my fingers on the desk right now, my anxiety is through the roof. 

Listen, I need your help, and I need it done perfectly. I'm a receptionist for the State Administration of Human Resource Programs here in PA, and my desk is currently a disaster zone. I spent weeks organizing a "Healthy Cooking & Balanced Lifestyle" seminar for our state employees. It's something I care deeply about—unlike my ex-husband who lived on junk food, but I digress. 

The seminar was yesterday. The problem? The temp workers completely botched the sign-in process and just dumped a bunch of files into the `visitor_logs` folder. 
The morning log is a messy CSV. Worse yet, the afternoon temp decided to use the new biometric badge scanners, which output these weird encrypted `.pa_badge` files. I have no idea how to read them! (Though I heard IT installed a `pa_badge_decoder` tool in our system).

I know for a fact that some people off the street snuck in just for the free quinoa salads! I need to weed them out. 

The biggest issue? IT just deleted our local `state_directory.json` file and migrated everything to the cloud. You will have to query the state employee database yourself to cross-reference the IDs. We have two command-line tools for this: the old `pa_hr_directory_legacy` and the new `pa_hr_directory_nextgen`. I'm pretty sure one of them is broken due to unpaid vendor bills, so please figure out which one works.

Here is what you need to do to stop my finger-tapping:
1. Decode all the visitor logs to get the full list of attended IDs.
2. Query the PA HR database tools to see which IDs actually belong to official state employees, and fetch their department codes.
3. Create a brand new folder called `audit_report`. 
4. Inside it, make me a beautifully organized `clean_attendance.csv` containing only the valid state employees who attended, along with their names and department codes. 
5. Then, create a separate `unauthorized.txt` file listing the IDs and Names of those gatecrashers who aren't in our directory. 

Please be thorough. I pride myself on having zero errors when the auditors come around. Thank you.
