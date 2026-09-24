import os

def build_env():
    os.makedirs("dictations", exist_ok=True)
    os.makedirs("front_desk", exist_ok=True)

    with open("dictations/monday_notes.txt", "w", encoding="utf-8") as f:
        f.write("Hey it's Tommy. *swish swish* Just dusting the Roosevelt statue. Did you know he gave a 90 minute speech after getting shot? Crazy! Anyway, volunteer signups. Little Timmy from the center, he's 12, wants to help for 3 hours. Sarah, she's 25, can do 4 hours. Okay, back to dusting.\n")

    with open("dictations/wednesday_notes.txt", "w", encoding="utf-8") as f:
        f.write("Oh god, oh man, the gala is tomorrow and I'm freaking out! Mr. Henderson, who is 60 by the way, said he'll bring his own mop for 5 hours. Jake is 17 and can do 2 hours, but he can't touch the bleach. I gotta remember that.\n")

    with open("dictations/friday_morning.txt", "w", encoding="utf-8") as f:
        f.write("*deep breaths* Okay, okay. Emily just called, she's 40, can give us 6 hours. That's good. Wait, where did I put my feather duster? Oh, it's under my arm. Okay. That's all the volunteers.\n")

if __name__ == "__main__":
    build_env()
