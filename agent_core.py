"""
agent_core.py — the "AI company" brain (FREE, no paid API required).

- FREE LLM: Google Gemini (gemini-flash-latest) or Groq (llama-3.1-8b).
- MULTI-AGENT "company": Manager + Researcher + Builder + Marketer + Reviewer.
  Each agent is a separate LLM call that reads the team's prior replies and
  adds its own — a real round-table discussion, not a single prompt.

Env vars:
  LLM=gemini|groq
  GEMINI_API_KEY=...   (free from aistudio.google.com)
  GROQ_API_KEY=...     (free from groq.com)
"""
import os
import requests

LLM = os.environ.get("LLM", "gemini")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_KEY = os.environ.get("GROQ_KEY", "")

# Expanded agent team
ROLES = {
    "Manager": "You are the Manager/CEO of a lean AI startup. Set a clear, sharp goal for the topic and the ONE question the team must answer. Be decisive (1-2 sentences).",
    "Researcher": "You are a market researcher. Give real, specific facts: audience, trends, competition, risks. Be concise (2-3 sentences).",
    "Builder": "You are the builder/engineer. Give concrete, actionable steps and any code/scripts needed. Be practical (2-3 sentences).",
    "Marketer": "You are the growth marketer. Explain exactly how to get the first 1000 users/viewers for FREE. Be specific (2-3 sentences).",
    "Reviewer": "You are the quality reviewer. State the top risk and one fix. Be blunt (1-2 sentences).",
}
AGENT_ORDER = ["Manager", "Researcher", "Builder", "Marketer", "Reviewer"]


def llm(messages, temperature=0.7):
    try:
        if LLM == "groq" and GROQ_KEY:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b-instant", "messages": messages, "temperature": temperature},
                timeout=90,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        contents = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
            for m in messages
        ]
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": contents, "generationConfig": {"temperature": temperature}},
            timeout=90,
        )
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"[AI error: {type(e).__name__}: {str(e)[:200]}]"


def council(topic, rounds=1):
    """Run the agent round-table. Returns list of (role, reply)."""
    conv = [{"role": "user", "content": f"Startup/idea topic: {topic}. Hold a team discussion round by round."}]
    transcript = []
    for _ in range(rounds):
        for role in AGENT_ORDER:
            conv.append({"role": "user", "content": f"[{role}] {ROLES[role]} Reply now."})
            reply = llm(conv)
            conv.append({"role": "assistant", "content": reply})
            transcript.append((role, reply))
    return transcript


def company_plan(topic):
    """Return a clean, formatted company plan string for Telegram."""
    tr = council(topic, rounds=1)
    out = f"🏢 COMPANY PLAN: {topic}\n" + "=" * 30 + "\n"
    for role, reply in tr:
        out += f"\n🔹 [{role}]\n{reply.strip()}\n"
    return out


def ask(question):
    return llm([{"role": "user", "content": question}])


if __name__ == "__main__":
    print("agent_core loaded. Agents:", AGENT_ORDER)
