import hashlib
import os

# ❌ Hardcoded secret
API_KEY = "12345-SECRET-KEY"

# ❌ Using eval
user_input = "2+2"
print(eval(user_input))

# ❌ Weak hash algorithm
password = "mypassword"
print(hashlib.md5(password.encode()).hexdigest())

# ❌ Insecure system call
os.system("ls " + user_input)
