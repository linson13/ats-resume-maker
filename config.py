# ==========================================================
# ⚙️ CONFIGURATION FILE
# Centralized constants and directory setup for all stages
# ==========================================================

import os

# ----------------------------------------------------------
# 🏗️ PROJECT DIRECTORY STRUCTURE
# ----------------------------------------------------------
# Dynamically detect base folder (works in Colab or local)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Core folders
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
# 🧠 MODEL CONFIGURATION
# ----------------------------------------------------------
# Model names (evaluators can change if needed)
GEMMA_MODEL_NAME = "google/gemma-2b-it"
LLAMA_MODEL_NAME = "meta-llama/Llama-3.2-3b-instruct"

# Hugging Face token placeholder (to be passed at runtime)
HF_TOKEN = None

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
