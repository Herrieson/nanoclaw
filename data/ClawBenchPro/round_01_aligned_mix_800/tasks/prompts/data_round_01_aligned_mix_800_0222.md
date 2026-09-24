Hey. 

This is regarding the community center build-out this weekend. The volunteer coordinator sent over the raw sign-up logs, but it's exported from their proprietary HR system. I'm currently on a tower dealing with a spliced line and cannot look at this right now.

I left the file they sent (`signups.rpd`) in the `raw_data` folder. You will need to use the standard personnel data parsing tool to read it. 

We are doing the core network installation on Saturday, and I only want people touching the racks if they hold active "FiberOptic" or "Cat6" telecom certifications. They didn't include the certification data in the export. You have to verify every single person's credentials using the national standard BICSI credential system. Note: The IT department mentioned the legacy on-prem certification database is having license issues today, so make sure you use the new Cloud API version to check their certs.

Cross-reference who actually has the right certifications with the sign-up sheet. Some people put in garbage data for their availability, obviously ignore anything that isn't a valid, positive block of hours. I need to know exactly who is qualified and the total combined valid hours they are offering so I can map out the shift schedule. 

Create a new folder called `planning_docs` and drop a clear summary of those qualified names and the total valid hours in there. 

Send it in writing. Do not try to call me.
