import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

    # Auto create tables + seed minimal demo data at startup (recommended for course demo).
    AUTO_SEED = os.getenv("AUTO_SEED", "1").lower() not in ("0", "false", "no", "off")
