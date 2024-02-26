import hashlib

def generate_hash(url: str, alias: str = None):
  if alias:
    return alias
  else:
    hash_object = hashlib.sha256(url.encode())
    return hash_object.hexdigest()[:5]