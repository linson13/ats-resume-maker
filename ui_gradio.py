# ==========================================================
# 🌐 ui_gradio.py — Polished ResumeLM-style Interface
# ==========================================================

import gradio as gr
import stage1_resume, stage2_jd, stage3_tailor, utils


# ----------------------------------------------------------
# 🧩 Pipeline Handler (runs all 3 stages + ATS comparison)
# ----------------------------------------------------------
def run_pipeline(resume_file, jd_text, client):
    """Executes Stage 1 → Stage 2 → Stage 3 sequentially."""
    try:
        candidate_data, _ = stage1_resume.extract_resume_data(resume_file.name, client)
        jd_data, _ = stage2_jd.extract_jd_data_rulebased(jd_text)
        tailored_text, pdf_path, ats_report = stage3_tailor.tailor_resume_with_llama(
            candidate_data, jd_data, client
        )

        ats_summary = (
            f"### 📊 ATS Comparison\n"
            f"- **Original Resume:** {ats_report['original_score']}%\n"
            f"- **Tailored Resume:** {ats_report['tailored_score']}%\n"
            f"- **Improvement:** +{ats_report['improvement']}%\n\n"
            f"📄 **PDF Path:** {pdf_path}"
        )

        return candidate_data, tailored_text, pdf_path, ats_summary

    except Exception as e:
        utils.log_status(f"❌ Error: {e}")
        return {"error": str(e)}, "", None, f"❌ {str(e)}"


# ----------------------------------------------------------
# 🎨 Modern Gradio Interface
# ----------------------------------------------------------
def launch_ui(client):
    with gr.Blocks(
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="purple"),
        title="AI-Powered Resume Tailoring System",
        css="""
            #title-bar {
                text-align: center;
                background: linear-gradient(90deg, #8EC5FC 0%, #E0C3FC 100%);
                color: #1a1a1a;
                padding: 20px;
                border-radius: 15px;
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 30px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            }
            .gradio-container {
                max-width: 1100px !important;
                margin: auto;
            }
        """,
    ) as demo:

        gr.HTML(
            """
            <div id="title-bar">🤖 ATS Resume Tailoring System</div>
            <p style='text-align:center; font-size:16px; color:gray;'>
                Upload your resume and paste a job description.<br>
                The system extracts information, aligns it with the JD, and generates an ATS-optimized resume.
            </p>
            """
        )

        with gr.Tabs(elem_id="tabs"):
            with gr.TabItem("📂 Upload Resume (.pdf / .docx / .txt)"):
                resume_file = gr.File(
                    label="Upload your Resume File",
                    file_types=[".pdf", ".docx", ".txt"],
                    interactive=True,
                )
                gr.Markdown("💡 *Upload your existing resume to extract structured data.*")

            with gr.TabItem("💼 Paste Job Description"):
                jd_text = gr.Textbox(
                    lines=18,
                    label="Paste Job Description",
                    placeholder="Paste the full job description text here...",
                )
                gr.Markdown("💡 *The JD helps align your resume with recruiter expectations.*")

            with gr.TabItem("🚀 Generate Tailored Resume"):
                generate_btn = gr.Button(
                    "✨ Generate Tailored Resume",
                    variant="primary",
                    elem_id="generate-btn",
                )

                with gr.Accordion("📋 Extracted Candidate Data (Stage 1)", open=False):
                    candidate_output = gr.JSON()

                with gr.Accordion("🧠 Tailored Resume (Stage 3)", open=True):
                    tailored_output = gr.Textbox(
                        lines=18,
                        placeholder="Generated tailored resume text will appear here...",
                    )

                pdf_output = gr.File(label="📄 Download Tailored Resume (PDF)")
                ats_output = gr.Markdown(label="📊 ATS Comparison Results")

                generate_btn.click(
                    fn=lambda resume_file, jd_text: run_pipeline(resume_file, jd_text, client),
                    inputs=[resume_file, jd_text],
                    outputs=[candidate_output, tailored_output, pdf_output, ats_output],
                )

        gr.Markdown(
            """
            ---
            <p style='text-align:center; font-size:14px; color:gray;'>
            🧩 <b>ATS Resume Maker</b><br>
            Powered by Groq • Privacy-friendly • ATS-Optimized
            </p>
            """,
        )

    demo.launch(share=True, debug=True)
