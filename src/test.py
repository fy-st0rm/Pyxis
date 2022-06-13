import hashlib, uuid
password = b"password"
salt = str(uuid.uuid4()).encode()
hashed_password = str(hashlib.sha512(password + salt).hexdigest())
print(hashed_password)
print(salt)
