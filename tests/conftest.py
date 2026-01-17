# Ensure project root is on sys.path so `from app...` imports work in tests
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Use file-based SQLite for tests to avoid in-memory connection isolation issues
TEST_DB_PATH = PROJECT_ROOT / "test.db"
# remove old test db to start clean
try:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
except Exception:
    # ignore if cannot delete; tests will still run with existing file
    pass

os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")
