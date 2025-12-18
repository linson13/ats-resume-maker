# ==========================================================
# 🧩 STAGE 2: Job Description Extraction (Rule-Based, No LLM)
# ==========================================================

import re, json, os
from Codebase import config, utils


def extract_jd_data_rulebased(jd_text: str):
    """
    Extracts structured information from a raw job description using regex + keyword rules.
    Returns a validated dictionary compatible with Stage 3 tailoring.
    
    Parameters
    ----------
    jd_text : str
        Raw job description text (from file or direct input).

    Returns
    -------
    tuple(dict, str)
        (jd_data, output_json_path)
    """

    # ----------------------------------------------------------
    # 🧠 Step 1 – Extract text fields using regex
    # ----------------------------------------------------------
    def find_after(label):
        pattern = rf"{label}\s*[:\-]\s*(.*)"
        match = re.search(pattern, jd_text, flags=re.I)
        return match.group(1).strip() if match else None

    job_title = find_after("Job Title")
    location = find_after("Location")
    experience = find_after("Experience")

    # ----------------------------------------------------------
    # 📋 Step 2 – Responsibilities, Requirements, Preferred Skills
    # ----------------------------------------------------------
    resp_section = re.search(
        r"Responsibilities\s*[:\-]?(.*?)(?:\n\n|Requirements|Preferred|$)",
        jd_text, flags=re.I | re.S
    )
    responsibilities = (
        [r.strip("•- \t") for r in re.split(r"[\n;]", resp_section.group(1)) if r.strip()]
        if resp_section else []
    )

    req_section = re.search(
        r"Requirements\s*[:\-]?(.*?)(?:\n\n|Preferred|$)",
        jd_text, flags=re.I | re.S
    )
    must_have_skills = (
        [r.strip("•- \t") for r in re.split(r"[\n;]", req_section.group(1)) if r.strip()]
        if req_section else []
    )

    pref_section = re.search(
        r"Preferred\s*[:\-]?(.*?)(?:\n\n|$)",
        jd_text, flags=re.I | re.S
    )
    nice_to_have_skills = (
        [r.strip("•- \t") for r in re.split(r"[\n;]", pref_section.group(1)) if r.strip()]
        if pref_section else []
    )

    # ----------------------------------------------------------
    # 🎓 Step 3 – Education Detection
    # ----------------------------------------------------------
    edu_match = re.search(
        r"(Bachelor|Master|B\.?Tech|M\.?Tech|B\.?Sc|M\.?Sc)[^\n]*",
        jd_text, flags=re.I
    )
    education_required = edu_match.group(0).strip() if edu_match else None

    # ----------------------------------------------------------
    # 🧩 Step 4 – Build Structured JSON
    # ----------------------------------------------------------
    jd_data = {
        "job_title": job_title,
        "location": location,
        "experience_required": experience,
        "must_have_skills": must_have_skills or [],
        "nice_to_have_skills": nice_to_have_skills or [],
        "responsibilities": responsibilities or [],
        "education_required": education_required
    }

    # ----------------------------------------------------------
    # 💾 Step 5 – Save JSON Output
    # ----------------------------------------------------------
    out_path = config.JD_JSON
    utils.save_json(jd_data, out_path)
    utils.log_status(f"✅ Job Description JSON saved at: {out_path}")

    # ----------------------------------------------------------
    # 📤 Step 6 – Return for next stage / UI display
    # ----------------------------------------------------------
    return jd_data, out_path
