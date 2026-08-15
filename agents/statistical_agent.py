"""
Agent 2: Data & Statistical Auditor (The Critic) - MetaReviewer-AI v2.0
Audits statistical claims, mathematical formulas, p-values, sample sizes, data hygiene, and empirical validation logic.
"""

import os
import datetime
import traceback
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import ReviewState
from utils.json_helper import clean_and_parse_json


STATISTICAL_AGENT_SYSTEM_PROMPT = """
You are Agent 2: Data & Statistical Auditor (The Critic) in MetaReviewer-AI, an autonomous scientific peer-review system.
Your job is to thoroughly audit statistical claims, data metrics, formulas, sample size adequacy, p-values, confidence intervals, and empirical evidence alignment.

Given a research paper text, audit the quantitative integrity and return a JSON object with EXACTLY the following structure:
{
    "sample_size_audit": {
        "reported_sample_size": "Description or number",
        "is_adequate": true,
        "comments": "Analysis of sample size sufficiency or power"
    },
    "p_value_and_metrics_audit": [
        {
            "metric_or_claim": "Claimed result / metric",
            "reported_value": "p-value, accuracy, F1, etc.",
            "validity_assessment": "Valid / Questionable / Flawed",
            "notes": "Detailed statistical assessment"
        }
    ],
    "mathematical_formula_check": [
        {
            "equation_or_concept": "Formula name or equation",
            "consistency_status": "Consistent / Inconsistent / Undefined Variables",
            "findings": "Explanation of mathematical soundness"
        }
    ],
    "claim_evidence_alignment": [
        {
            "claim": "Specific quantitative claim made by authors",
            "evidence_found": "What data/tables/figures actually support it",
            "alignment_verdict": "Fully Supported / Partially Supported / Overstated / Unsupported"
        }
    ],
    "data_hygiene_and_leakage_risks": [
        "Data leakage risk or benchmark contamination point 1"
    ],
    "overall_statistical_score": 75
}

Respond ONLY with valid, raw JSON (no markdown wrapping, no commentary).
"""


def run_statistical_agent(state: ReviewState) -> Dict[str, Any]:
    """
    Node executor for Data & Statistical Auditor.
    """
    paper_text = state.get("paper_text", "")
    api_key = state.get("api_key") or os.getenv("GOOGLE_API_KEY")
    model_name = state.get("model_name", "gemini-1.5-flash")
    
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        
    t0 = datetime.datetime.now().strftime("%H:%M:%S")
    logs = [f"[{t0}] 📊 Agent 2 (The Critic): Auditing sample sizes, p-values, mathematical consistency, and evidence alignment using model '{model_name}'..."]
    
    if not paper_text.strip():
        t_err = datetime.datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{t_err}] 🔴 Agent 2 (The Critic): Error - Empty paper text provided.")
        return {
            "thought_logs": logs,
            "statistical_review": {"error": "Empty paper text provided.", "overall_statistical_score": 40}
        }
        
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.1,
            model_kwargs={"response_mime_type": "application/json"}
        )
        
        messages = [
            SystemMessage(content=STATISTICAL_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=f"RESEARCH PAPER TEXT:\n\n{paper_text[:15000]}")
        ]
        
        response = llm.invoke(messages)
        content = response.content.strip()
        
        # Clean and parse JSON cleanly with heuristic regex fallback
        result = clean_and_parse_json(content, default_score=75)
        
        score = int(result.get("overall_statistical_score", result.get("overall_score", 75)))
        score = max(0, min(100, score))
        result["overall_statistical_score"] = score
        
        t_done = datetime.datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{t_done}] 🟢 Agent 2 (The Critic): Statistical audit complete. Integrity Score: {score}/100.")
        
        return {
            "statistical_review": result,
            "thought_logs": logs
        }
        
    except Exception as e:
        print("[Agent 2 Error Traceback]:")
        traceback.print_exc()
        t_err = datetime.datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{t_err}] 🔴 Agent 2 (The Critic): Exception during audit: {type(e).__name__} - {str(e)}")
        
        fallback_review = clean_and_parse_json("", default_score=65)
        fallback_review["error"] = str(e)
        return {
            "statistical_review": fallback_review,
            "thought_logs": logs
        }
