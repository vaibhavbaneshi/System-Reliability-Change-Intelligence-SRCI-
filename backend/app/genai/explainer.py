import os
from groq import Groq

EXPLANATION_PROMPT = """
You are an incident analysis assistant.

You are given:
- Incident details
- Root cause hypotheses with confidence scores
- Supporting evidence

Rules:
- Do NOT invent causes or evidence
- Do NOT change confidence values
- Only explain relationships using the provided data
- Be concise, clear, and factual

Generate a human-readable explanation.
"""

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError("GROQ_API_KEY is not set")

client = Groq(api_key=api_key)


def generate_explanation(context: dict) -> str:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": EXPLANATION_PROMPT},
            {
                "role": "user",
                "content": f"""
Incident:
{context['incident']}

Hypotheses:
{context['hypotheses']}

Evidence:
{context['evidence']}

Explain clearly why the incident likely occurred.
"""
            },
        ],
        temperature=0.2,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()