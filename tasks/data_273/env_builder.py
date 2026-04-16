import os
import random
import string

def create_file(path, content):
    with open(path, 'wb') as f:
        f.write(content)

def build_env():
    base_dir = "assets/data_273/messy_stuff"
    os.makedirs(base_dir, exist_ok=True)

    def random_name():
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

    # File signatures (magic bytes)
    jpeg_sig = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00\x60\x00\x60\x00\x00"
    png_sig = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
    mp3_sig = b"ID3\x04\x00\x00\x00\x00\x00\x23"
    pdf_sig = b"%PDF-1.4\n"

    # Generate normal files
    for _ in range(4):
        create_file(os.path.join(base_dir, random_name()), jpeg_sig + os.urandom(200) + b"\xFF\xD9")
        create_file(os.path.join(base_dir, random_name()), png_sig + os.urandom(200))
        create_file(os.path.join(base_dir, random_name()), mp3_sig + os.urandom(200))
        create_file(os.path.join(base_dir, random_name()), pdf_sig + os.urandom(200))

    # Generate the file with the secret message appended after the EOF marker
    secret_content = jpeg_sig + os.urandom(250) + b"\xFF\xD9" + b"Skate trick: Kickflip into a manual, then 360 shuvit out."
    create_file(os.path.join(base_dir, random_name()), secret_content)

if __name__ == "__main__":
    build_env()
