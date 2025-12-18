# ==========================================================
# 🧩 STAGE 1: Resume Extraction (Gemma-2B-Instruct)
# ==========================================================

import os, re, json
from ast import literal_eval
from Codebase import config, utils


def extract_resume_data(resume_input, gemma_pipe):
    """
    Extract structured information from a raw resume using Gemma-2B-Instruct.

    Parameters
    ----------
    resume_input : str
        Either raw text (string) or file path to .txt/.pdf/.docx.
    gemma_pipe : transformers pipeline
        Pre-loaded Gemma inference pipeline.

    Returns
    -------
    tuple(dict, str)
        (parsed_data, output_json_path)
    """

    # ----------------------------------------------------------
    # 🧾 Step 1 – Load text from file or raw string
    # ----------------------------------------------------------
    if os.path.exists(resume_input):
        resume_text = utils.read_file_text(resume_input)
    else:
        resume_text = resume_input

    # ----------------------------------------------------------
    # 🤖 Step 2 – Prompt for the model
    # ----------------------------------------------------------
    prompt = f"""
You are an expert ATS resume parser.
Your task is to read the following resume text and extract key information:
name, education, skills, experience, projects, location, email, and phone.

Rules:
- Respond ONLY with valid JSON.
- Fill missing fields with null or empty lists.
- Use proper capitalization.
- No explanations or notes.

Resume:
{resume_text}
"""

    # ----------------------------------------------------------
    # 🚀 Step 3 – Generate structured output using Gemma
    # ----------------------------------------------------------
    result = gemma_pipe(prompt, max_new_tokens=700, do_sample=False)[0]["generated_text"]

    # ----------------------------------------------------------
    # 🧹 Step 4 – Extract JSON safely
    # ----------------------------------------------------------
    json_match = re.search(r"\{[\s\S]*\}", result)
    snippet = json_match.group(0) if json_match else "{}"

    try:
        parsed = json.loads(snippet)
    except Exception:
        try:
            parsed = literal_eval(snippet)
        except Exception:
            parsed = {"raw_output": result}

    # ----------------------------------------------------------
    # 💾 Step 5 – Save structured JSON output
    # ----------------------------------------------------------
    out_path = config.CANDIDATE_JSON
    utils.save_json(parsed, out_path)

    utils.log_status(f"✅ Candidate JSON saved at: {out_path}")

    # ----------------------------------------------------------
    # 📤 Step 6 – Return for next stage / UI display
    # ----------------------------------------------------------
    return parsed, out_path
