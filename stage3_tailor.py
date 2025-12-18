# ==========================================================
# 🧩 STAGE 3: Tailored Resume Generation (LLaMA + Predefined Template)
# ==========================================================

import os, re, json
from Codebase import config, utils
from Codebase.BaseCVTemplate import build_cv_from_data


# -----------------------------
# 🧹 Clean Model Output
# -----------------------------
def _clean_output(raw: str) -> str:
    """Cleans unwanted prompt residues, notes, and formatting issues."""
    # Remove leftover prompt instructions or rules
    raw = re.sub(r"CANDIDATE DATA:.*?Now write the tailored resume below:", "", raw, flags=re.S | re.I)
    raw = re.sub(r"JOB DESCRIPTION DATA:.*?$", "", raw, flags=re.S | re.I)
    raw = re.sub(r"(?i)rules\s*:.*?(?=\n[A-Z])", "", raw, flags=re.S)

    # Remove note/disclaimer lines at the end
    raw = re.sub(r"(?i)note\s*:.*", "", raw, flags=re.S)

    # Remove double "Education" or "Summary" that appear twice
    raw = re.sub(r"(?i)(education\s*education)", "Education", raw)
    raw = re.sub(r"(?i)(summary\s*summary)", "Summary", raw)

    # Normalize markdown symbols and stray bullets
    raw = re.sub(r"[*_#>`]+", "", raw)
    raw = re.sub(r"\n\s*•\s*", "\n• ", raw)  # proper bullet spacing
    raw = re.sub(r"•{2,}", "•", raw)         # remove duplicate bullets

    # Normalize punctuation
    repl = {"–": "-", "—": "-", "•": "•", "“": '"', "”": '"', "‘": "'", "’": "'"}
    for k, v in repl.items():
        raw = raw.replace(k, v)

    # Remove empty lines or stray spaces
    raw = re.sub(r"\n{3,}", "\n\n", raw).strip()
    return raw.strip()


# -----------------------------
# 🧩 Split into sections
# -----------------------------
def _segment_sections(text: str):
    """Splits LLaMA output into logical resume sections based on headers."""
    pattern = r"(?mi)^(CONTACT|SUMMARY|SKILLS|PROJECTS|EXPERIENCE|EDUCATION)\s*:?\s*$"
    chunks = re.split(pattern, text)
    sections = {}
    for i in range(1, len(chunks), 2):
        title = chunks[i].strip().upper()
        body = chunks[i + 1].strip()
        sections[title] = body
    return sections


# -----------------------------
# 📊 ATS Comparison Utility
# -----------------------------
def compute_ats_score(resume_text: str, jd_keywords: list[str]) -> float:
    """Simple keyword match score between resume and JD keywords."""
    jd_set = set(word.lower() for word in jd_keywords if word.strip())
    resume_words = set(resume_text.lower().split())
    matched = sum(1 for word in jd_set if word in resume_words)
    return round((matched / len(jd_set)) * 100, 2) if jd_set else 0.0


# -----------------------------
# 🚀 Main Function
# -----------------------------
def tailor_resume_with_llama(candidate_input, jd_input, llama_pipe, output_pdf_path=None):
    """
    Uses LLaMA to generate a tailored, ATS-friendly resume and formats it using the predefined BaseCVTemplate.

    Returns
    -------
    tuple(str, str, dict)
        (tailored_resume_text, output_pdf_path, ats_report)
    """

    # 1️⃣ Load candidate & JD data
    if isinstance(candidate_input, str) and os.path.exists(candidate_input):
        candidate_data = utils.load_json(candidate_input)
    else:
        candidate_data = candidate_input

    if isinstance(jd_input, str) and os.path.exists(jd_input):
        jd_data = utils.load_json(jd_input)
    else:
        jd_data = jd_input

    # 2️⃣ Build Prompt
    prompt = f"""
You are an expert resume writer specializing in ATS-friendly formatting.
Tailor the candidate's resume for the provided job description.

Follow this section structure:
NAME
CONTACT
SUMMARY
SKILLS
PROJECTS
EXPERIENCE
EDUCATION

Rules:
- No markdown or tables.
- Use concise, bullet-style phrasing.
- Focus on measurable, impactful statements.
- Align skills and experience with the job description.

CANDIDATE DATA:
{json.dumps(candidate_data, indent=2)}

JOB DESCRIPTION DATA:
{json.dumps(jd_data, indent=2)}

Now write the tailored resume below:
"""

    # 3️⃣ Generate text
    utils.log_status("🧠 Generating tailored resume using LLaMA model...")
    result = llama_pipe(prompt, max_new_tokens=900, temperature=0.4, do_sample=True)[0]["generated_text"]

    # 4️⃣ Clean & Segment
    text = _clean_output(result)
    sections = _segment_sections(text)

    # 5️⃣ Determine output PDF path
    if not output_pdf_path:
        candidate_name = (
            candidate_data.get("name")
            or candidate_data.get("full_name")
            or "candidate"
        )
        output_pdf_path = utils.get_pdf_output_path(candidate_name)

    # 6️⃣ Build PDF using predefined template
    utils.log_status("🖋️ Building ATS-friendly formatted PDF...")
    build_cv_from_data(candidate_data, sections, output_pdf_path)
    utils.log_status(f"✅ Tailored resume saved at: {output_pdf_path}")

    # 7️⃣ ⚖️ Compute ATS Comparison (Dynamic Keyword Extraction)
    def extract_keywords(jd_dict):
        """
        Dynamically collects all possible keywords from the JD dictionary.
        Works even if key names differ (skills, requirements, responsibilities, etc.)
        """
        keywords = []
        for key, value in jd_dict.items():
            if isinstance(value, list):
                keywords.extend(value)
            elif isinstance(value, str):
                keywords.extend(re.findall(r"[A-Za-z]+", value))
        keywords = [kw.lower() for kw in keywords if len(kw) > 2]
        return list(set(keywords))

    jd_keywords = extract_keywords(jd_data)

    # Build textual corpus for original and tailored resumes
    original_text = " ".join([
        str(candidate_data.get("skills", "")),
        str(candidate_data.get("projects", "")),
        str(candidate_data.get("experience", "")),
    ])
    tailored_text_clean = text

    # Compute ATS scores
    original_score = compute_ats_score(original_text, jd_keywords)
    tailored_score = compute_ats_score(tailored_text_clean, jd_keywords)
    ats_improvement = round(tailored_score - original_score, 2)

    ats_report = {
        "original_score": original_score,
        "tailored_score": tailored_score,
        "improvement": ats_improvement,
        "jd_keywords": jd_keywords[:20]  # optional preview
    }

    utils.log_status(
        f"📊 ATS Comparison → Original: {original_score}% | Tailored: {tailored_score}% | Improvement: +{ats_improvement}%"
    )

    # 8️⃣ Return results
    return text, output_pdf_path, ats_report
