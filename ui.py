import streamlit as st
from config import GROQ_API_KEY, MODEL_OPTIONS, CUSTOM_CSS
from extractor import extract_text
from ai_engine import Groq, get_client, run_analysis, run_chat


def apply_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def init_state():
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""
    if "resume_name" not in st.session_state:
        st.session_state.resume_name = ""
    if "jd_text" not in st.session_state:
        st.session_state.jd_text = ""
    if "analysis" not in st.session_state:
        st.session_state.analysis = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🧭 Career Companion")
        st.caption("AIML-03 • Hackathon")
        st.divider()

        model_name = st.selectbox("AI Model", list(MODEL_OPTIONS.keys()))
        model = MODEL_OPTIONS[model_name]

        st.divider()
        st.markdown("### How it works")
        st.markdown("""
        ① Upload resume  
        ② Paste job description  
        ③ Run scan  
        ④ Check skill gaps  
        ⑤ Ask Career Assistant
        """)
        st.divider()

        if GROQ_API_KEY:
            st.success("AI Engine Connected")
        else:
            st.error("GROQ_API_KEY not found")

        st.divider()
        if st.button("🧹 Clear Session", use_container_width=True):
            st.session_state.resume_text = ""
            st.session_state.resume_name = ""
            st.session_state.jd_text = ""
            st.session_state.analysis = None
            st.session_state.chat_history = []
            st.rerun()

    return model


def render_header():
    st.markdown('<div class="kicker">AI RESUME & CAREER COMPANION</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">The Scan</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Analyze your resume against a target job and discover your skill gaps.</div>', unsafe_allow_html=True)
    st.divider()


def render_results():
    analysis = st.session_state.analysis
    if not analysis:
        st.info("Upload a resume and job description, then run the scan.")
        return

    # SCORE
    score = analysis.get("fit_score", 0)
    verdict = analysis.get("verdict", "Analysis Complete")

    st.markdown('<div class="card score">', unsafe_allow_html=True)
    st.markdown(f'<div class="score-number">{score}</div>', unsafe_allow_html=True)
    st.markdown('<div class="score-label">FIT SCORE</div>', unsafe_allow_html=True)
    st.subheader(verdict)
    st.markdown('</div>', unsafe_allow_html=True)

    # SUMMARY
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">Assessment</div>', unsafe_allow_html=True)
    st.write(analysis.get("summary", "No summary available."))
    st.markdown('</div>', unsafe_allow_html=True)

    # SKILLS
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="label">✓ Matched Skills</div>', unsafe_allow_html=True)
        matched = analysis.get("matched_skills", [])
        if matched:
            for skill in matched:
                st.markdown(f'<span class="tag match">✓ {skill}</span>', unsafe_allow_html=True)
        else:
            st.write("No clear matched skills found.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="label">✗ Missing Skills</div>', unsafe_allow_html=True)
        missing = analysis.get("missing_skills", [])
        if missing:
            for skill in missing:
                st.markdown(f'<span class="tag gap">✗ {skill}</span>', unsafe_allow_html=True)
        else:
            st.write("No major skill gaps found.")
        st.markdown('</div>', unsafe_allow_html=True)

    # SUGGESTIONS
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="label">✎ Suggested Improvements</div>', unsafe_allow_html=True)
    suggestions = analysis.get("suggestions", [])
    if suggestions:
        for suggestion in suggestions:
            title = suggestion.get("title", "Improvement")
            detail = suggestion.get("detail", "")
            st.markdown(f'<div class="suggestion"><b>{title}</b><br>{detail}</div>', unsafe_allow_html=True)
    else:
        st.write("No suggestions available.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ATS
    ats_notes = analysis.get("ats_notes", "")
    if ats_notes:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="label">⚠ ATS Notes</div>', unsafe_allow_html=True)
        st.write(ats_notes)
        st.markdown('</div>', unsafe_allow_html=True)


def render_analyze_tab(model):
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<div class="label">EXHIBIT A — RESUME</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

        if uploaded_file:
            text, error = extract_text(uploaded_file)
            if error:
                st.error(error)
            else:
                st.session_state.resume_text = text
                st.session_state.resume_name = uploaded_file.name
                st.success(f"Resume loaded: {uploaded_file.name}")
                st.caption(f"{len(text.split())} words extracted")

        st.markdown('<div class="label">EXHIBIT B — JOB DESCRIPTION</div>', unsafe_allow_html=True)
        st.session_state.jd_text = st.text_area(
            "Paste Job Description",
            value=st.session_state.jd_text,
            height=260,
            placeholder="Paste the target job description here..."
        )

        run_scan = st.button("🔍 Run the Scan", use_container_width=True)

    with right:
        if run_scan:
            if not GROQ_API_KEY:
                st.error("GROQ_API_KEY is missing from your .env file.")
            elif Groq is None:
                st.error("Groq is not installed. Run: pip install groq")
            elif not st.session_state.resume_text:
                st.error("Please upload a resume first.")
            elif not st.session_state.jd_text.strip():
                st.error("Please paste a job description first.")
            else:
                with st.spinner("🤖 AI is analyzing your resume..."):
                    try:
                        client = get_client()
                        result = run_analysis(
                            client,
                            model,
                            st.session_state.resume_text,
                            st.session_state.jd_text
                        )
                        st.session_state.analysis = result
                        st.success("Analysis completed!")
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

        render_results()


def render_chat_tab(model):
    st.subheader("💬 Career Assistant")
    st.caption("Ask questions about your resume, skills, interviews, or career.")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask your career question...")
    if not prompt:
        return

    if not GROQ_API_KEY:
        st.error("GROQ_API_KEY is missing from your .env file.")
        return

    if Groq is None:
        st.error("Groq is not installed. Run: pip install groq")
        return

    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                client = get_client()
                reply = run_chat(
                    client,
                    model,
                    st.session_state.chat_history,
                    st.session_state.resume_text,
                    st.session_state.jd_text
                )
            except Exception as e:
                reply = f"Error: {e}"

        st.markdown(reply)

    st.session_state.chat_history.append({"role": "assistant", "content": reply})