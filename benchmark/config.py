from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Directories
DATASETS_DIR = BASE_DIR / "datasets"
RUNS_DIR = BASE_DIR / "runs"

# Test cases file
TEST_CASES_FILE = DATASETS_DIR / "test_cases.json"

# Database URL for SQLite
DATABASE_URL = f"sqlite:///{BASE_DIR / 'benchmark.db'}"