# Ensure project root is on sys.path so `from app...` imports work in tests
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Also set DATABASE_URL to in-memory SQLite for tests by default
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

