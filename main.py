# ==========================================================
# 🚀 MAIN ORCHESTRATOR
# Capstone_Project-HPPCS01
# ==========================================================

import argparse, os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from transformers import pipeline
from Codebase import config, utils, stage1_resume, stage2_jd, stage3_tailor




def load_models(hf_token: str):
    """
    Loads both Gemma (for resume extraction) and LLaMA (for tailoring).
    Returns two pipeline objects: gemma_pipe, llama_pipe
    """

    utils.log_status("🔄 Loading Gemma-2B-Instruct model for resume extraction...")
    gemma_pipe = pipeline(
        "text2text-generation",
        model=config.GEMMA_MODEL_NAME,
        token=hf_token
    )

    utils.log_status("🔄 Loading LLaMA model for resume tailoring...")
    llama_pipe = pipeline(
        "text-generation",
        model=config.LLAMA_MODEL_NAME,
        token=hf_token
    )

    return gemma_pipe, llama_pipe


def run_cli_mode(gemma_pipe, llama_pipe):
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
    candidate_data, candidate_json = stage1_resume.extract_resume_data(resume_file, gemma_pipe)

    # ---------------- Stage 2 ----------------
    utils.log_status("🧾 Parsing job description...")
    with open(jd_file, "r", encoding="utf-8") as f:
        jd_text = f.read()
    jd_data, jd_json = stage2_jd.extract_jd_data_rulebased(jd_text)

    # ---------------- Stage 3 ----------------
    utils.log_status("🧠 Generating tailored resume...")
    tailored_text, pdf_path, ats_report = stage3_tailor.tailor_resume_with_llama(candidate_data, jd_data, llama_pipe)

    # ---------------- Completion ----------------
    utils.log_status("✅ Pipeline completed successfully!")
    print(f"\n📁 Candidate JSON: {candidate_json}")
    print(f"📁 Job Description JSON: {jd_json}")
    print(f"📄 Tailored Resume PDF: {pdf_path}")
    print(f"\n📊 ATS Comparison: Original {ats_report['original_score']}% → Tailored {ats_report['tailored_score']}% (+{ats_report['improvement']}%)\n")


def run_gradio_mode(gemma_pipe, llama_pipe):
    """Launches the Gradio interface for interactive testing."""
    utils.log_status("🧠 Launching Gradio Interface...")
    from Codebase import ui_gradio
    ui_gradio.launch_ui(gemma_pipe, llama_pipe)


def main():
    # ------------------------------------------------------
    # 🧭 Parse Arguments
    # ------------------------------------------------------
    parser = argparse.ArgumentParser(description="Capstone Resume Tailoring Pipeline")
    parser.add_argument("--hf_token", type=str, help="Your Hugging Face access token")
    parser.add_argument("--ui_mode", type=str, default="cli", help="'cli' or 'gradio'")
    args = parser.parse_args()

    # ------------------------------------------------------
    # 🔐 Token Management
    # ------------------------------------------------------
    # Use passed token, environment variable, or default local token
    hf_token = args.hf_token or os.getenv("HF_TOKEN") or "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"
    config.HF_TOKEN = hf_token
    utils.log_status("🔐 Hugging Face token loaded successfully (using environment or CLI arg).")

    # ------------------------------------------------------
    # 🧱 Load Models
    # ------------------------------------------------------
    gemma_pipe, llama_pipe = load_models(hf_token)

    # ------------------------------------------------------
    # 🚀 Choose Mode
    # ------------------------------------------------------
    if args.ui_mode.lower() == "gradio":
        run_gradio_mode(gemma_pipe, llama_pipe)
    else:
        run_cli_mode(gemma_pipe, llama_pipe)


if __name__ == "__main__":
    main()
