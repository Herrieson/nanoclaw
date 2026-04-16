Hey there! Oh man, I am so glad you're here. I'm kind of freaking out right now. 

So, I recently took a break from my regular RN job to focus on volunteering, and I'm organizing this huge free community health screening event tomorrow. It's super important for the neighborhood! But... the registration data got totally scrambled by the ancient laptop we were using. I guess that's what I get for volunteering to handle the "tech" stuff when my expertise is literally just taking vital signs and telling bad medical jokes, right? Ha. Ha. *sweats profusely*

Anyway, I managed to salvage a folder of weird log files in `registrations/`. I need to prep triage packets tonight for anyone who might be at high risk, but I can't read these logs manually—there are too many and my anxiety is through the roof. 

Could you please dig through those logs and find anyone with a blood pressure over 140/90 (if *either* the top number is strictly over 140 *or* the bottom number is strictly over 90) OR a resting heart rate strictly over 100? 

I just need you to make a CSV file called `urgent_patients.csv` in the `./` directory. It should have the headers `Name`, `Age`, and `Phone`. 
Oh, and please also make a `summary.txt` in the same `./` folder with just the total number of these urgent cases (like literally just the number), so I know how many red folders to print while I stress-drink this enormous iced Vietnamese coffee.

Thank you SO much. You're saving my life. Literally! Well, figuratively, but you get it.
