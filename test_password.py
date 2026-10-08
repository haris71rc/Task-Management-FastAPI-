from app.core.security import (
    hash_password,
    verify_password,
)


password = "MyStrongPassword123!"

hashed = hash_password(password)
hasss=hash_password("MyStrongPassword123!")

print("Hash:")
print(hashed)

print("Hash2:")
print(hasss)

print(
    "Correct:",
    verify_password(
        password,
        hashed,
    ),
)

print(
    "Wrong:",
    verify_password(
        "WrongPassword",
        hashed,
    ),
)