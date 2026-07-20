# ATS Resume Maker & Scoring System

An ATS-aware resume generation and scoring system that parses resumes, analyzes job descriptions, and produces optimized, ATS-friendly resume versions using NLP, LLMs, and rule-based heuristics.

---

## 🚀 Project Overview

Applicant Tracking Systems (ATS) often reject resumes due to poor keyword alignment and formatting issues.  
This project addresses that problem by building an end-to-end automation pipeline that:

- Parses unstructured resumes
- Extracts and analyzes job description requirements
- Scores resumes based on ATS heuristics
- Generates tailored, ATS-optimized resume versions

The system combines **rule-based NLP techniques** with **LLM-assisted tailoring** to improve resume relevance and ATS compatibility.

---

## 🧠 Key Features

- Resume parsing and structured information extraction  
- Job description (JD) parsing and keyword analysis  
- ATS score computation using keyword matching and formatting heuristics  
- Resume tailoring using LLM-assisted rewriting  
- Interactive UI for generating and comparing resume variants  

---

## 🏗️ System Architecture

The project is implemented as a multi-stage pipeline:

1. **Stage 1 — Resume Extraction** (`stage1_resume.py`): parses an uploaded `.pdf` / `.docx` / `.txt` resume into structured JSON (name, skills, experience, projects, etc.) using an LLM call via [Groq](https://groq.com).
2. **Stage 2 — JD Parsing** (`stage2_jd.py`): rule-based extraction of job title, required/preferred skills, responsibilities, and education from a pasted job description. No LLM call needed here.
3. **Stage 3 — Tailoring** (`stage3_tailor.py`): sends the candidate + JD JSON to Groq, gets back tailored resume sections, computes a keyword-based ATS score before/after, and renders a one-page PDF via `BaseCVTemplate.py` (ReportLab).

`main.py` runs the pipeline either in CLI mode (using the sample files in `input/`) or launches a Gradio UI (`ui_gradio.py`) for interactive use.

Uses Groq's API rather than local models — no GPU or large model downloads required.

---

## ⚙️ Setup

```bash
git clone https://github.com/linson13/ats-resume-maker.git
cd ats-resume-maker
pip install -r requirements.txt

cp .env.example .env
# then edit .env and add your GROQ_API_KEY (free at https://console.groq.com/keys)
```

## ▶️ Usage

CLI mode (runs against `input/sample_resume.txt` and `input/sample_jd.txt`):
```bash
python main.py --ui_mode cli
```

Gradio UI (upload your own resume, paste a JD):
```bash
python main.py --ui_mode gradio
```

Generated files land in `output/structured_json/` and `output/tailored_pdfs/`.

## 🔐 Security note

Never commit a `.env` file or hardcode API keys in source files — `.env` is gitignored. If you ever accidentally push a real key, revoke/rotate it immediately at the provider's dashboard.
