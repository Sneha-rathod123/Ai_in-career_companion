import json
import re
from config import GROQ_API_KEY, ANALYSIS_PROMPT, CHAT_PROMPT

try:
    from groq import Groq
except ImportError:
    Groq = None


def get_client():
    if Groq is None or not GROQ_API_KEY:
        return None
    return Groq(api_key=GROQ_API_KEY)


def run_analysis(client, model, resume, job_description):
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
            {"role": "system", "content": ANALYSIS_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=1800,
        response_format={"type": "json_object"}
    )

    result = response.choices[0].message.content
    result = re.sub(r"```json|```", "", result).strip()
    return json.loads(result)


def run_chat(client, model, history, resume, job_description):
    context = f"""
Candidate Resume:
{resume[:5000]}

Job Description:
{job_description[:3000]}
"""

    messages = [{"role": "system", "content": CHAT_PROMPT + context}]
    messages.extend(history)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.5,
        max_tokens=1000
    )

    return response.choices[0].message.content