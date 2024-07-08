from werkzeug.security import generate_password_hash, check_password_hash

password = "mysecretpassword"

# Generate hash
hash1 = generate_password_hash(password)
hash2 = generate_password_hash(password)

print(hash1)
print(hash2)

# Verify the password
is_correct1 = check_password_hash(hash1, password)
is_correct2 = check_password_hash(hash2, password)

print(is_correct1)  # Should be True
print(is_correct2)  # Should be True
