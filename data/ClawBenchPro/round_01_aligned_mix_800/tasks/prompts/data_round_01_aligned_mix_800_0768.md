Look, I don't have the energy to sugarcoat this—my toddler has been crying for an hour, I'm working on three hours of sleep, and my store manager just dropped a massive headache on my lap. 

I work customer service at this retail chain, and I've been pushing them for months to take our "Cultural Diversity and Accessibility" initiative seriously. They finally collected customer feedback, but whoever exported the data from our dinosaur-era POS system completely botched it. 

The files are dumped in a folder called `raw_feedback`. Some of it is somewhat readable, but other files are just lines of gibberish because the system encodes things in Base64 for absolutely no logical reason. 

I need you to dig through that entire `raw_feedback` folder. Decode whatever needs decoding. Read through all the feedback and find every single entry that explicitly mentions the words "diversity" or "accessibility" (case shouldn't matter, people type how they type). 

Once you find them, I need a clean, professional JSON file placed inside a new `deliverables` directory. I need to know exactly how many matching entries there are, and I need a list of the customers' names along with their exact feedback text. Do whatever you have to do to parse it, just get it done quickly so I can email this to corporate and get back to my kid.
