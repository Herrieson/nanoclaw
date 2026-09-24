import sys

def extract():
    # Simulate extraction of the binary data in env_builder
    data = [
        "Name,Skills,Availability",
        "David,first_aid,guiding,Mon",
        "Samuel,clearing,hauling,Wed",
        "Marie,cooking,clearing,Thu",
        "Chloe,guiding,crowd_control,Sat",
        "Jerome,first_aid,painting,Wed"
    ]
    print("\n".join(data))

if __name__ == "__main__":
    extract()
