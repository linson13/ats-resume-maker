# ==========================================================
# 🧰 utils.py
# Helper utilities for I/O, JSON handling, file reading, and logging
# ==========================================================

import os, json
from Codebase import config
from docx import Document
from PyPDF2 import PdfReader


# ----------------------------------------------------------
# 💾 JSON Utilities
# ----------------------------------------------------------
def save_json(data: dict, path: str):
    """Save a dictionary as a pretty JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(path: str) -> dict:
    """Load and return JSON content from a file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------------------------
# 📄 Resume / JD File Text Extraction
# ----------------------------------------------------------
def read_file_text(file_path: str) -> str:
    """
    Read text content from .txt, .pdf, or .docx files.
    Raises ValueError for unsupported types.
    """
    ext = os.path.splitext(file_path)[-1].lower()

    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    elif ext == ".pdf":
        pdf = PdfReader(file_path)
        text = []
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        return "\n".join(text)

    elif ext == ".docx":
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        raise ValueError("Unsupported file type. Please upload .txt, .pdf, or .docx.")


# ----------------------------------------------------------
# 🧩 Path Helpers (for saving outputs consistently)
# ----------------------------------------------------------
def get_candidate_json_path():
    return config.CANDIDATE_JSON


def get_jd_json_path():
    return config.JD_JSON


def get_pdf_output_path(candidate_name: str = "candidate"):
    """Generate dynamic PDF output path based on candidate name."""
    safe_name = candidate_name.replace(" ", "_")
    return os.path.join(config.TAILORED_PDF_DIR, f"tailored_resume_{safe_name}.pdf")


# ----------------------------------------------------------
# 🧠 Logging Helper
# ----------------------------------------------------------
def log_status(msg: str):
    """Uniform status messages for CLI and Gradio."""
    print(f"[INFO] {msg}")
