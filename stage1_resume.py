# ==========================================================
# 🧩 STAGE 1: Resume Extraction (Groq LLM)
# ==========================================================

import os
import config
import utils
import llm_client

SYSTEM_PROMPT = """You are an expert ATS resume parser.
Read the resume text and extract structured candidate data.
Respond ONLY with a JSON object using exactly these keys:
name, email, phone, location, education, skills, experience, projects.
- "skills" must be a list of strings.
- "education", "experience", "projects" must be lists of strings (one entry per item).
- Fill missing fields with null (for strings) or [] (for lists).
- Do not include any commentary outside the JSON object."""


def extract_resume_data(resume_input, client=None):
    """
    Extract structured information from a raw resume using an LLM.

    Parameters
    ----------
    resume_input : str
        Either raw text (string) or a file path to .txt/.pdf/.docx.
    client : groq.Groq, optional
        Reuse an existing client; a new one is created if not passed.

    Returns
    -------
    tuple(dict, str)
        (parsed_data, output_json_path)
    """
    client = client or llm_client.get_client()

    # Step 1 – Load text from file or raw string
    if os.path.exists(resume_input):
        resume_text = utils.read_file_text(resume_input)
    else:
        resume_text = resume_input

    # Step 2 – Ask the LLM for structured JSON directly (no regex scraping)
    utils.log_status("🔍 Extracting candidate data with Groq...")
    parsed = llm_client.generate_json(
        client,
        SYSTEM_PROMPT,
        f"Resume:\n{resume_text}",
    )

    # Step 3 – Save structured JSON output
    out_path = config.CANDIDATE_JSON
    utils.save_json(parsed, out_path)
    utils.log_status(f"✅ Candidate JSON saved at: {out_path}")

    return parsed, out_path
