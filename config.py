# ==========================================================
# ⚙️ CONFIGURATION FILE
# Centralized constants and directory setup for all stages
# ==========================================================

import os
from dotenv import load_dotenv

load_dotenv()  # reads GROQ_API_KEY etc. from a local .env file

# ----------------------------------------------------------
# 🏗️ PROJECT DIRECTORY STRUCTURE
# ----------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
STRUCTURED_JSON_DIR = os.path.join(OUTPUT_DIR, "structured_json")
TAILORED_PDF_DIR = os.path.join(OUTPUT_DIR, "tailored_pdfs")

# ----------------------------------------------------------
# 📁 FILE PATHS
# ----------------------------------------------------------
CANDIDATE_JSON = os.path.join(STRUCTURED_JSON_DIR, "candidate_output.json")
JD_JSON = os.path.join(STRUCTURED_JSON_DIR, "job_description.json")
DEFAULT_TAILORED_PDF = os.path.join(TAILORED_PDF_DIR, "tailored_resume.pdf")

# ----------------------------------------------------------
# 🧠 LLM CONFIGURATION (Groq — no local model downloads needed)
# ----------------------------------------------------------
# GROQ_API_KEY must be set as an environment variable or in a local .env file.
# NEVER hardcode API keys in source files.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model used for both resume extraction and tailoring.
# llama-3.3-70b-versatile is a strong general-purpose choice on Groq's free tier.
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")

# ----------------------------------------------------------
# 🧾 FOLDER INITIALIZATION
# ----------------------------------------------------------
for path in [INPUT_DIR, STRUCTURED_JSON_DIR, TAILORED_PDF_DIR]:
    os.makedirs(path, exist_ok=True)


# ----------------------------------------------------------
# ✅ LOGGING UTILITY
# ----------------------------------------------------------
def show_structure():
    """Utility to confirm that all folders exist."""
    print(f"📁 Base Directory: {BASE_DIR}")
    print(f"├── Input: {INPUT_DIR}")
    print(f"├── Output: {OUTPUT_DIR}")
    print(f"│   ├── JSON: {STRUCTURED_JSON_DIR}")
    print(f"│   └── PDFs: {TAILORED_PDF_DIR}")
    print("✅ Folder structure verified.\n")


def require_api_key():
    """Fail fast with a clear message instead of a confusing API error later."""
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Create a .env file (see .env.example) "
            "or export GROQ_API_KEY in your shell before running."
        )
