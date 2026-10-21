import os

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "development-secret-key-change-later"
)

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60