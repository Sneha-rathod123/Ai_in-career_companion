import os
from dotenv import load_dotenv

load_dotenv()

# API Keys & Models
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_OPTIONS = {
    "GPT-OSS 120B": "openai/gpt-oss-120b",
    "Llama 3.3 70B": "llama-3.3-70b-versatile"
}

# System Prompts
ANALYSIS_PROMPT = """
You are an expert technical recruiter and career coach.

Compare the candidate's resume with the job description.

Return ONLY valid JSON in this exact structure:

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

# Styling
CUSTOM_CSS = """
<style>
.stApp {
    background-color: #0B1014;
}

section[data-testid="stSidebar"] {
    background-color: #0D141C;
    border-right: 1px solid rgba(255,255,255,0.08);
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}

.kicker {
    color: #5EEAD4;
    font-family: monospace;
    font-size: 13px;
    letter-spacing: 2px;
}

.hero-title {
    font-size: 42px;
    font-weight: 700;
    margin-top: 5px;
    margin-bottom: 5px;
}

.subtitle {
    color: #A9B2BC;
    font-size: 17px;
}

.card {
    background-color: #121922;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 18px;
}

.label {
    color: #A9B2BC;
    font-family: monospace;
    font-size: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.score {
    text-align: center;
}

.score-number {
    color: #5EEAD4;
    font-family: monospace;
    font-size: 60px;
    font-weight: bold;
}

.score-label {
    color: #A9B2BC;
    font-family: monospace;
}

.tag {
    display: inline-block;
    padding: 6px 10px;
    margin: 4px;
    border-radius: 15px;
    font-family: monospace;
    font-size: 12px;
}

.match {
    color: #5EEAD4;
    background: rgba(94,234,212,0.10);
    border: 1px solid rgba(94,234,212,0.30);
}

.gap {
    color: #FF7777;
    background: rgba(255,119,119,0.10);
    border: 1px solid rgba(255,119,119,0.30);
}

.suggestion {
    border-left: 3px solid #FFB454;
    background: rgba(255,180,84,0.07);
    padding: 12px;
    margin-bottom: 10px;
    border-radius: 0 6px 6px 0;
}
</style>
"""