import hashlib
import time

def generate_hash(url: str, alias: str = None):
  if alias:
    return alias
  else:
    timestamp = str(time.time())
    input = url + timestamp
    hash_object = hashlib.sha256(input.encode())
    return hash_object.hexdigest()[:5]