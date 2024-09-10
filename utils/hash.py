import hashlib

# Function to compute file hash (e.g., SHA-256)
# hashing takes really short time, by testing 5 MB < 0.01s, so ignore time spent here
def compute_file_hash(file) -> str:

    hasher = hashlib.sha256()
    chunk = file.read(8192)
    while chunk:
        hasher.update(chunk)
        chunk = file.read(8192)
    # By GPT: Python 3.8+ can use walrus operator ":="
    # while chunk := file.read(8192):
    #     hasher.update(chunk)
    file.seek(0)  # Reset file pointer after reading

    return hasher.hexdigest()