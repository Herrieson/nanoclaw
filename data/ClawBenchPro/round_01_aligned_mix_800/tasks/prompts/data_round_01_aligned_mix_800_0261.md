*Adjusts sunglasses* Hola amigo! Yeah, I know I'm wearing shades indoors, but the fluorescent lights in this depot give me a serious headache, plus they make me look cool, right? 

Listen, I need your help. My dispatcher, Dave—I swear his glasses must be made of frosted glass—completely scrambled today's delivery manifests. I'm handling the premium business accounts today, and I am *extremely* particular about my route. 

Dave dumped all the batch files into the `manifests` folder. Here is the nightmare:
1. They are in completely different formats.
2. Dave's system export bugged out, so the files **only have tracking numbers and addresses**, no Zone or Priority information!
3. One of the scanners spat out a weird encrypted terminal file (`batch_C.dat`).

Here's the deal: I only deliver to **Zone 7** today. But Dave mixed in packages for Zone 3 and Zone 9! Plus, there are VIP packages mixed in there that need to be prioritized. 

**Your Mission:**
1. Decode that `.dat` file using the system's `manifest_decoder_skill`.
2. Find out the Zone and VIP status for *every single package* based on its address. You'll need to use the routing APIs installed on the system. (Hint: Dave mentioned something about `dave_legacy_router_skill`, but he hasn't paid the software bill in months, so you might need to find the `smart_geo_router_skill` as a backup).
3. Create a clean digital sheet or report for my own route, showing *only* the Zone 7 packages, and you absolutely must put the VIP packages at the very top of that list so I hit them first. Put my final organized route in a new folder called `clean_route`. 
4. In that same `clean_route` folder, leave me a separate list of just the tracking numbers for the out-of-zone packages. I'm going to hand them back to Dave with a big smile and a joke about getting his eyes checked. 

Please hurry and script this out or whatever you need to do. I gotta finish this run perfectly so I can pick up my kids from school and hit the gym! Gracias!
