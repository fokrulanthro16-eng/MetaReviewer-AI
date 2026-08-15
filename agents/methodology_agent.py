"""
Agent 1: Methodology & Claim Inspector (The Skeptic) - MetaReviewer-AI v2.0
Extracts key hypotheses, methodology steps, core scientific claims, methodological ambiguities, unstated assumptions, and limitations.
"""

import os
import datetime
import traceback
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import ReviewState
from utils.json_helper import clean_and_parse_json


METHODOLOGY_AGENT_SYSTEM_PROMPT = """
You are Agent 1: Methodology & Claim Inspector (The Skeptic) in MetaReviewer-AI, an autonomous scientific peer-review system.
Your job is to rigorously inspect research paper methodology with a critical, skeptical eye.

Given a research paper text, perform a deep architectural & methodological audit and return a JSON object with EXACTLY the following structure:
{
    "paper_summary": "Concise 2-3 sentence overview of what the paper aims to achieve",
    "key_hypotheses": ["Hypothesis 1", "Hypothesis 2"],
    "core_scientific_claims": [
        {
            "claim_id": "C1",
            "statement": "Claim statement extracted from paper",
            "section": "Methodology / Results",
            "initial_verdict": "Supported & Verifiable / Weak Evidence / Methodologically Flawed",
            "confidence_level": "High / Medium / Low"
        }
    ],
    "methodology_steps": [
        {"step_number": 1, "title": "Title", "description": "Details", "rigor_score": 8}
    ],
    "methodological_ambiguities": [
        {"area": "Area name", "issue": "Specific missing or vague description", "severity": "High / Medium / Low"}
    ],
    "unstated_assumptions": [
        "Unstated assumption 1",
        "Unstated assumption 2"
    ],
    "identified_limitations": [
        "Limitation 1",
        "Limitation 2"
    ],
    "overall_methodology_score": 75
}

Respond ONLY with valid, raw JSON (no markdown wrapping, no commentary).
"""


def run_methodology_agent(state: ReviewState) -> Dict[str, Any]:
    """
    Node executor for Methodology & Claim Inspector.
    """
    paper_text = state.get("paper_text", "")
    api_key = state.get("api_key") or os.getenv("GOOGLE_API_KEY")
    model_name = state.get("model_name", "gemini-1.5-flash")
    
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        
    t0 = datetime.datetime.now().strftime("%H:%M:%S")
    logs = [f"[{t0}] 🕵️ Agent 1 (The Skeptic): Inspecting methodology, claims, and unstated assumptions using model '{model_name}'..."]
    
    if not paper_text.strip():
        t_err = datetime.datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{t_err}] 🔴 Agent 1 (The Skeptic): Error - Empty paper text provided.")
        return {
            "thought_logs": logs,
            "methodology_review": {"error": "Empty paper text provided.", "overall_methodology_score": 40}
        }
        
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.1,
            model_kwargs={"response_mime_type": "application/json"}
        )
        
        messages = [
            SystemMessage(content=METHODOLOGY_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=f"RESEARCH PAPER TEXT:\n\n{paper_text[:15000]}")
        ]
        
        response = llm.invoke(messages)
        content = response.content.strip()
        
        # Clean and parse JSON cleanly with heuristic regex fallback
        result = clean_and_parse_json(content, default_score=75)
        
        score = int(result.get("overall_methodology_score", result.get("overall_score", 75)))
        score = max(0, min(100, score))
        result["overall_methodology_score"] = score
        
        t_done = datetime.datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{t_done}] 🟢 Agent 1 (The Skeptic): Methodology inspection complete. Rigor Score: {score}/100.")
        
        return {
            "methodology_review": result,
            "thought_logs": logs
        }
        
    except Exception as e:
        print("[Agent 1 Error Traceback]:")
        traceback.print_exc()
        t_err = datetime.datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{t_err}] 🔴 Agent 1 (The Skeptic): Exception during audit: {type(e).__name__} - {str(e)}")
        
        fallback_review = clean_and_parse_json("", default_score=65)
        fallback_review["error"] = str(e)
        return {
            "methodology_review": fallback_review,
            "thought_logs": logs
        }
