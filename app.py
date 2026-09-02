import os
import io
import json
import re

import streamlit as st
from dotenv import load_dotenv

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    import docx
except ImportError:
    docx = None

try:
    from groq import Groq
except ImportError:
    Groq = None


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Resume & Career Companion",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_OPTIONS = {
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "Llama 3.3 70B": "llama-3.3-70b-versatile"
}


# ============================================================
# PREMIUM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 5% 5%, rgba(94,234,212,.10), transparent 25%),
        radial-gradient(circle at 95% 15%, rgba(99,102,241,.10), transparent 28%),
        #070B10;
}

.block-container {
    max-width: 1250px;
    padding-top: 1.4rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background: #091018;
    border-right: 1px solid rgba(255,255,255,.08);
}

section[data-testid="stSidebar"] h2 {
    color: #5EEAD4;
}

.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 12px;
    border: 1px solid rgba(94,234,212,.25);
    background: linear-gradient(135deg,#123C3A,#17273A);
    color: white;
    font-weight: 700;
    transition: .25s;
}

.stButton > button:hover {
    border-color: #5EEAD4;
    box-shadow: 0 0 25px rgba(94,234,212,.18);
    transform: translateY(-2px);
}

.stTextArea textarea {
    background: #0C131B !important;
    color: white !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,.10) !important;
}

.stFileUploader {
    background: rgba(255,255,255,.025);
    border-radius: 14px;
}

button[data-baseweb="tab"] {
    font-weight: 700;
    font-size: 15px;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #5EEAD4 !important;
}

hr {
    border-color: rgba(255,255,255,.07);
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HERO
# ============================================================

st.html("""
<div style="
    position:relative;
    overflow:hidden;
    padding:34px 38px;
    border-radius:26px;
    margin-bottom:26px;
    background:
        radial-gradient(circle at 90% 50%, rgba(94,234,212,.14), transparent 25%),
        linear-gradient(135deg,#101A22,#0B1118);
    border:1px solid rgba(255,255,255,.10);
    box-shadow:0 20px 60px rgba(0,0,0,.35);
">

    <div style="
        color:#5EEAD4;
        font-family:monospace;
        font-size:12px;
        letter-spacing:3px;
        font-weight:bold;
        margin-bottom:8px;
    ">
        AI RESUME & CAREER COMPANION
    </div>

    <div style="
        font-size:46px;
        font-weight:800;
        line-height:1.1;
        margin-bottom:10px;
        background:linear-gradient(90deg,#ffffff,#5EEAD4,#818CF8);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
    ">
        The Career Scan
    </div>

    <div style="
        color:#A9B2BC;
        font-size:16px;
        max-width:720px;
        line-height:1.6;
    ">
        Analyze your resume against a target job, discover skill gaps,
        improve ATS compatibility and prepare for your next opportunity.
    </div>

    <div style="
        position:absolute;
        right:55px;
        top:30px;
        width:150px;
        height:150px;
        border-radius:50%;
        display:flex;
        align-items:center;
        justify-content:center;
        background:radial-gradient(circle,rgba(94,234,212,.22),rgba(94,234,212,.03),transparent 70%);
        border:1px solid rgba(94,234,212,.20);
        box-shadow:0 0 45px rgba(94,234,212,.10);
    ">

        <div style="
            font-size:76px;
            filter:drop-shadow(0 0 18px rgba(94,234,212,.45));
        ">
            🤖
        </div>

    </div>

</div>
""")


# ============================================================
# SESSION STATE
# ============================================================

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


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    with st.sidebar:

        st.markdown("## 🤖 Career Companion")

        st.caption("AIML-03 • AI Career Intelligence")

        st.divider()

        model_name = st.selectbox(
            "🧠 AI Model",
            list(MODEL_OPTIONS.keys())
        )

        model = MODEL_OPTIONS[model_name]

        st.divider()

        st.markdown("### 🚀 Workflow")

        st.markdown("""
        **01** 📄 Upload Resume

        **02** 🎯 Add Job Description

        **03** 🔍 Run AI Scan

        **04** 📊 Analyze Skill Gaps

        **05** 🤖 Ask Career AI
        """)

        st.divider()

        if GROQ_API_KEY:
            st.success("🟢 AI ENGINE ONLINE")
        else:
            st.error("🔴 GROQ_API_KEY NOT FOUND")

        st.divider()

        if st.button("🧹 Clear Session"):

            st.session_state.resume_text = ""
            st.session_state.resume_name = ""
            st.session_state.jd_text = ""
            st.session_state.analysis = None
            st.session_state.chat_history = []

            st.rerun()

    return model


# ============================================================
# FILE EXTRACTION
# ============================================================

def extract_text(uploaded_file):

    filename = uploaded_file.name.lower()
    data = uploaded_file.read()

    if filename.endswith(".pdf"):

        if pdfplumber is None:
            return None, "pdfplumber is not installed."

        try:

            text = []

            with pdfplumber.open(io.BytesIO(data)) as pdf:

                for page in pdf.pages:

                    page_text = page.extract_text()

                    if page_text:
                        text.append(page_text)

            return "\n".join(text).strip(), None

        except Exception as e:
            return None, str(e)

    if filename.endswith(".docx"):

        if docx is None:
            return None, "python-docx is not installed."

        try:

            document = docx.Document(io.BytesIO(data))

            text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
                if paragraph.text.strip()
            )

            return text.strip(), None

        except Exception as e:
            return None, str(e)

    if filename.endswith(".txt"):

        return (
            data.decode(
                "utf-8",
                errors="ignore"
            ).strip(),
            None
        )

    return None, "Please upload PDF, DOCX or TXT."


# ============================================================
# AI PROMPTS
# ============================================================

ANALYSIS_PROMPT = """
You are an expert technical recruiter and career coach.

Compare the candidate's resume with the job description.

Return ONLY valid JSON:

{
    "fit_score": 0,
    "verdict": "Strong Match",
    "summary": "Short assessment",
    "matched_skills": [],
    "missing_skills": [],
    "suggestions": [
        {
            "title": "Short title",
            "detail": "Actionable advice"
        }
    ],
    "ats_notes": "Short ATS advice"
}

Rules:

- fit_score must be between 0 and 100.
- Maximum 8 matched skills.
- Maximum 8 missing skills.
- Maximum 5 suggestions.
- Do not invent candidate experience.
- Be practical and specific.
"""

CHAT_PROMPT = """
You are an AI career assistant.

Help the candidate with:

- Resume improvement
- Job preparation
- Interview preparation
- Skill gaps
- Projects
- Learning roadmap
- Career questions

Give practical and concise answers.

Do not claim that a resume score guarantees employment.
"""


# ============================================================
# GROQ CLIENT
# ============================================================

def get_client():

    if Groq is None:
        return None

    if not GROQ_API_KEY:
        return None

    return Groq(api_key=GROQ_API_KEY)


# ============================================================
# ANALYSIS
# ============================================================

def run_analysis(
    client,
    model,
    resume,
    job_description
):

    prompt = f"""
RESUME:

{resume[:10000]}

JOB DESCRIPTION:

{job_description[:6000]}

Compare the resume with the job description.

Return ONLY valid JSON.
"""

    response = client.chat.completions.create(

        model=model,

        messages=[
            {
                "role": "system",
                "content": ANALYSIS_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2,
        max_tokens=1800,

        response_format={
            "type": "json_object"
        }
    )

    result = response.choices[0].message.content

    result = re.sub(
        r"```json|```",
        "",
        result
    ).strip()

    return json.loads(result)


# ============================================================
# CHAT
# ============================================================

def run_chat(
    client,
    model,
    history,
    resume,
    job_description
):

    context = f"""
Candidate Resume:

{resume[:5000]}

Job Description:

{job_description[:3000]}
"""

    messages = [
        {
            "role": "system",
            "content": CHAT_PROMPT + context
        }
    ]

    messages.extend(history)

    response = client.chat.completions.create(

        model=model,
        messages=messages,
        temperature=0.5,
        max_tokens=1000
    )

    return response.choices[0].message.content


# ============================================================
# RESULTS
# ============================================================

def render_results():

    analysis = st.session_state.analysis

    if not analysis:

        st.info(
            "🤖 Upload your resume + job description and run the AI scan."
        )

        return

    score = analysis.get("fit_score", 0)

    verdict = analysis.get(
        "verdict",
        "Analysis Complete"
    )

    # SCORE CARD

    st.html(f"""
    <div style="
        text-align:center;
        padding:30px;
        margin:5px 0 20px;
        border-radius:22px;
        background:
            radial-gradient(circle,rgba(94,234,212,.12),transparent 60%),
            #101820;
        border:1px solid rgba(94,234,212,.18);
        box-shadow:0 0 45px rgba(94,234,212,.06);
    ">

        <div style="font-size:42px;">🤖</div>

        <div style="
            color:#5EEAD4;
            font-family:monospace;
            font-size:72px;
            font-weight:800;
            line-height:1;
        ">
            {score}
        </div>

        <div style="
            color:#8995A2;
            font-family:monospace;
            font-size:11px;
            letter-spacing:3px;
        ">
            AI FIT SCORE / 100
        </div>

        <div style="
            font-size:22px;
            font-weight:700;
            margin-top:12px;
        ">
            {verdict}
        </div>

    </div>
    """)

    # SUMMARY

    with st.container(border=True):

        st.markdown("### 🤖 AI Assessment")

        st.write(
            analysis.get(
                "summary",
                "No summary available."
            )
        )

    # SKILLS

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):

            st.markdown("### ✅ Matched Skills")

            matched = analysis.get(
                "matched_skills",
                []
            )

            if matched:

                st.write(" • ".join(
                    [f"✓ {x}" for x in matched]
                ))

            else:

                st.write(
                    "No clear matched skills found."
                )

    with col2:

        with st.container(border=True):

            st.markdown("### ⚠️ Missing Skills")

            missing = analysis.get(
                "missing_skills",
                []
            )

            if missing:

                st.write(" • ".join(
                    [f"✗ {x}" for x in missing]
                ))

            else:

                st.write(
                    "No major skill gaps found."
                )

    # SUGGESTIONS

    with st.container(border=True):

        st.markdown("### 🚀 AI Improvement Plan")

        suggestions = analysis.get(
            "suggestions",
            []
        )

        if suggestions:

            for i, suggestion in enumerate(
                suggestions,
                1
            ):

                title = suggestion.get(
                    "title",
                    "Improvement"
                )

                detail = suggestion.get(
                    "detail",
                    ""
                )

                st.info(
                    f"**{i}. {title}**\n\n{detail}"
                )

        else:

            st.write(
                "No suggestions available."
            )

    # ATS

    ats_notes = analysis.get(
        "ats_notes",
        ""
    )

    if ats_notes:

        with st.container(border=True):

            st.markdown("### ⚡ ATS Intelligence")

            st.write(ats_notes)


# ============================================================
# ANALYZE TAB
# ============================================================

def render_analyze_tab(model):

    left, right = st.columns(
        [1, 1],
        gap="large"
    )

    with left:

        st.markdown("#### 📄 YOUR RESUME")

        uploaded_file = st.file_uploader(
            "Upload Resume",
            type=[
                "pdf",
                "docx",
                "txt"
            ]
        )

        if uploaded_file:

            text, error = extract_text(
                uploaded_file
            )

            if error:

                st.error(error)

            else:

                st.session_state.resume_text = text

                st.session_state.resume_name = (
                    uploaded_file.name
                )

                st.success(
                    f"✓ {uploaded_file.name} loaded"
                )

                st.caption(
                    f"📊 {len(text.split())} words extracted"
                )

        st.markdown("#### 🎯 TARGET JOB")

        st.session_state.jd_text = st.text_area(
            "Job Description",
            value=st.session_state.jd_text,
            height=280,
            placeholder="Paste the target job description here..."
        )

        run_scan = st.button(
            "🤖 RUN AI CAREER SCAN"
        )

    with right:

        if run_scan:

            if not GROQ_API_KEY:

                st.error(
                    "GROQ_API_KEY is missing from your .env file."
                )

            elif Groq is None:

                st.error(
                    "Groq is not installed. Run: pip install groq"
                )

            elif not st.session_state.resume_text:

                st.error(
                    "📄 Please upload a resume first."
                )

            elif not st.session_state.jd_text.strip():

                st.error(
                    "🎯 Please paste a job description first."
                )

            else:

                with st.spinner(
                    "🤖 Robo AI is scanning your career profile..."
                ):

                    try:

                        client = get_client()

                        result = run_analysis(
                            client,
                            model,
                            st.session_state.resume_text,
                            st.session_state.jd_text
                        )

                        st.session_state.analysis = result

                        st.success(
                            "🤖 AI Scan Completed!"
                        )

                    except Exception as e:

                        st.error(
                            f"Analysis failed: {e}"
                        )

        render_results()


# ============================================================
# ROBO ASSISTANT
# ============================================================

def render_chat_tab(model):

    st.html("""
    <div style="
        padding:25px;
        margin-bottom:20px;
        border-radius:20px;
        background:linear-gradient(135deg,#101B22,#0C1219);
        border:1px solid rgba(255,255,255,.08);
    ">

        <div style="
            display:flex;
            align-items:center;
            gap:18px;
        ">

            <div style="
                font-size:60px;
                filter:drop-shadow(0 0 15px rgba(94,234,212,.35));
            ">
                🤖
            </div>

            <div>

                <div style="
                    font-size:25px;
                    font-weight:800;
                ">
                    Robo Career Assistant
                </div>

                <div style="
                    color:#8B96A3;
                    margin-top:5px;
                ">
                    Resume • Interview • Skills • Projects • Career
                </div>

            </div>

        </div>

    </div>
    """)

    for message in st.session_state.chat_history:

        avatar = (
            "🤖"
            if message["role"] == "assistant"
            else "👤"
        )

        with st.chat_message(
            message["role"],
            avatar=avatar
        ):

            st.markdown(
                message["content"]
            )

    prompt = st.chat_input(
        "Ask Robo anything about your career..."
    )

    if not prompt:
        return

    if not GROQ_API_KEY:

        st.error(
            "GROQ_API_KEY is missing from your .env file."
        )

        return

    if Groq is None:

        st.error(
            "Groq is not installed. Run: pip install groq"
        )

        return

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.markdown(prompt)

    with st.chat_message(
        "assistant",
        avatar="🤖"
    ):

        with st.spinner("🤖 Robo is thinking..."):

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

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": reply
        }
    )


# ============================================================
# MAIN
# ============================================================

def main():

    init_state()

    model = render_sidebar()

    tabs = st.tabs([
        "📄  Career Scan",
        "🤖  Robo Assistant"
    ])

    with tabs[0]:

        render_analyze_tab(model)

    with tabs[1]:

        render_chat_tab(model)

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    st.caption(
        "🤖 AI Resume & Career Companion • AIML-03 Hackathon • Powered by Groq"
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()