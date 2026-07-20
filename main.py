# ==========================================================
# 🚀 MAIN ORCHESTRATOR
# ATS Resume Maker
# ==========================================================

import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import config
import utils
import stage1_resume
import stage2_jd
import stage3_tailor
import llm_client


def run_cli_mode(client):
    """Executes the full pipeline sequentially using sample files from /input."""
    utils.log_status("🧩 Running in CLI Mode...")
    config.show_structure()

    resume_file = os.path.join(config.INPUT_DIR, "sample_resume.txt")
    jd_file = os.path.join(config.INPUT_DIR, "sample_jd.txt")

    if not os.path.exists(resume_file) or not os.path.exists(jd_file):
        print("❌ Missing sample files in /input/. Please add 'sample_resume.txt' and 'sample_jd.txt'.")
        return

    # ---------------- Stage 1 ----------------
    utils.log_status("🔍 Extracting candidate data from resume...")
    candidate_data, candidate_json = stage1_resume.extract_resume_data(resume_file, client)

    # ---------------- Stage 2 ----------------
    utils.log_status("🧾 Parsing job description...")
    with open(jd_file, "r", encoding="utf-8") as f:
        jd_text = f.read()
    jd_data, jd_json = stage2_jd.extract_jd_data_rulebased(jd_text)

    # ---------------- Stage 3 ----------------
    utils.log_status("🧠 Generating tailored resume...")
    tailored_text, pdf_path, ats_report = stage3_tailor.tailor_resume_with_llama(
        candidate_data, jd_data, client
    )

    # ---------------- Completion ----------------
    utils.log_status("✅ Pipeline completed successfully!")
    print(f"\n📁 Candidate JSON: {candidate_json}")
    print(f"📁 Job Description JSON: {jd_json}")
    print(f"📄 Tailored Resume PDF: {pdf_path}")
    print(
        f"\n📊 ATS Comparison: Original {ats_report['original_score']}% → "
        f"Tailored {ats_report['tailored_score']}% (+{ats_report['improvement']}%)\n"
    )


def run_gradio_mode(client):
    """Launches the Gradio interface for interactive testing."""
    utils.log_status("🧠 Launching Gradio Interface...")
    import ui_gradio
    ui_gradio.launch_ui(client)


def main():
    parser = argparse.ArgumentParser(description="ATS Resume Tailoring Pipeline")
    parser.add_argument("--ui_mode", type=str, default="cli", help="'cli' or 'gradio'")
    args = parser.parse_args()

    # Fails fast with a clear message if GROQ_API_KEY isn't set — see .env.example
    client = llm_client.get_client()

    if args.ui_mode.lower() == "gradio":
        run_gradio_mode(client)
    else:
        run_cli_mode(client)


if __name__ == "__main__":
    main()
