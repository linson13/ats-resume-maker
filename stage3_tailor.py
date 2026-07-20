# ==========================================================
# 🧩 STAGE 3: Tailored Resume Generation (Groq LLM + PDF Template)
# ==========================================================

import os
import re
import json
import config
import utils
import llm_client
from BaseCVTemplate import build_cv_from_data

SYSTEM_PROMPT = """You are an expert resume writer specializing in ATS-friendly resumes.
Tailor the candidate's resume to the job description provided.
Respond ONLY with a JSON object using exactly these keys, each a single string
(use \\n between bullet points within a section, no markdown, no tables):
CONTACT, SUMMARY, SKILLS, PROJECTS, EXPERIENCE, EDUCATION.
Focus on concise, measurable, impactful statements aligned with the job description."""


# -----------------------------
# 📊 ATS Comparison Utility
# -----------------------------
def compute_ats_score(resume_text: str, jd_keywords: list) -> float:
    """Simple keyword match score between resume and JD keywords."""
    jd_set = set(word.lower() for word in jd_keywords if word.strip())
    resume_words = set(resume_text.lower().split())
    matched = sum(1 for word in jd_set if word in resume_words)
    return round((matched / len(jd_set)) * 100, 2) if jd_set else 0.0


def _extract_keywords(jd_dict: dict) -> list:
    """Dynamically collects all possible keywords from the JD dictionary."""
    keywords = []
    for value in jd_dict.values():
        if isinstance(value, list):
            keywords.extend(value)
        elif isinstance(value, str):
            keywords.extend(re.findall(r"[A-Za-z]+", value))
    return list({kw.lower() for kw in keywords if len(kw) > 2})


# -----------------------------
# 🚀 Main Function
# -----------------------------
def tailor_resume_with_llama(candidate_input, jd_input, client=None, output_pdf_path=None):
    """
    Uses an LLM to generate a tailored, ATS-friendly resume and formats it
    using the predefined BaseCVTemplate.

    Returns
    -------
    tuple(str, str, dict)
        (tailored_resume_text, output_pdf_path, ats_report)
    """
    client = client or llm_client.get_client()

    # 1️⃣ Load candidate & JD data
    candidate_data = utils.load_json(candidate_input) if (
        isinstance(candidate_input, str) and os.path.exists(candidate_input)
    ) else candidate_input

    jd_data = utils.load_json(jd_input) if (
        isinstance(jd_input, str) and os.path.exists(jd_input)
    ) else jd_input

    # 2️⃣ Generate tailored sections as structured JSON
    utils.log_status("🧠 Generating tailored resume with Groq...")
    user_prompt = (
        f"CANDIDATE DATA:\n{json.dumps(candidate_data, indent=2)}\n\n"
        f"JOB DESCRIPTION DATA:\n{json.dumps(jd_data, indent=2)}"
    )
    sections = llm_client.generate_json(client, SYSTEM_PROMPT, user_prompt,
                                         temperature=0.4, max_tokens=1800)
    # Normalize keys to uppercase to match BaseCVTemplate's SECTION_ORDER
    sections = {str(k).upper(): str(v) for k, v in sections.items()}
    text = "\n\n".join(f"{k}\n{v}" for k, v in sections.items())

    # 3️⃣ Determine output PDF path
    if not output_pdf_path:
        candidate_name = candidate_data.get("name") or candidate_data.get("full_name") or "candidate"
        output_pdf_path = utils.get_pdf_output_path(candidate_name)

    # 4️⃣ Build PDF using predefined template
    utils.log_status("🖋️ Building ATS-friendly formatted PDF...")
    build_cv_from_data(candidate_data, sections, output_pdf_path)
    utils.log_status(f"✅ Tailored resume saved at: {output_pdf_path}")

    # 5️⃣ ATS Comparison
    jd_keywords = _extract_keywords(jd_data)
    original_text = " ".join([
        str(candidate_data.get("skills", "")),
        str(candidate_data.get("projects", "")),
        str(candidate_data.get("experience", "")),
    ])
    original_score = compute_ats_score(original_text, jd_keywords)
    tailored_score = compute_ats_score(text, jd_keywords)
    ats_improvement = round(tailored_score - original_score, 2)

    ats_report = {
        "original_score": original_score,
        "tailored_score": tailored_score,
        "improvement": ats_improvement,
        "jd_keywords": jd_keywords[:20],
    }
    utils.log_status(
        f"📊 ATS Comparison → Original: {original_score}% | Tailored: {tailored_score}% | "
        f"Improvement: +{ats_improvement}%"
    )

    return text, output_pdf_path, ats_report
