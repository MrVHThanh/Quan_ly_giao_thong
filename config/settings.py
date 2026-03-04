# config/settings.py

import os
from pathlib import Path

# =========================
# BASE DIRECTORY
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# ENVIRONMENT
# =========================

DEBUG = True

# =========================
# DATABASE
# =========================

DATABASE_DIR = BASE_DIR / "database"
DATABASE_NAME = "giaothong.db"
DATABASE_PATH = DATABASE_DIR / DATABASE_NAME

# =========================
# DATA FOLDERS
# =========================

DATA_DIR = BASE_DIR / "data"
SEED_DIR = BASE_DIR / "seeds"

# =========================
# LOGGING
# =========================

LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"