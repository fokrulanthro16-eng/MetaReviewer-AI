"""
Agent 3: Lead Arbiter & Consensus Synthesizer - MetaReviewer-AI v2.0
Reconciles findings from Methodology Inspector and Statistical Auditor, synthesizes the v2.0 Multi-Agent Debate Trace, Claims Matrix, and 5-Step Author Improvement Roadmap.
"""

import os
import json
import datetime
import traceback
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from agents.state import ReviewState
from utils.json_helper import clean_and_parse_json


ARBITER_AGENT_SYSTEM_PROMPT = """
You are Agent 3: Lead Arbiter & Consensus Synthesizer in MetaReviewer-AI, an autonomous scientific peer-review system.
You receive the audit findings from:
1. Agent 1 (Methodology & Claim Inspector - The Skeptic)
2. Agent 2 (Data & Statistical Auditor - The Critic)

Your job is to:
1. Perform a structured debate & reconciliation between Skeptic and Critic findings.
2. Produce an Overall Reproducibility Score (0-100) along with 5 component sub-scores (0-100):
   - Methodology Rigor
   - Statistical Integrity
   - Empirical Replicability
   - Data & Code Transparency
   - Theoretical Soundness
3. Synthesize a 3-Step Interactive Multi-Agent Debate Trace:
   - Step 1: Agent 1 (Skeptic) raises methodological concern
   - Step 2: Agent 2 (Critic) identifies statistical/math/empirical anomaly
   - Step 3: Agent 3 (Arbiter) resolves the conflict into actionable consensus
4. Construct a Claim-by-Claim Verification Matrix for extracted paper claims with verdicts:
   - "Supported & Verifiable" OR "Weak Evidence / Unstated Assumption" OR "Methodologically Flawed / Inconclusive"
5. Formulate a 5-Step Prioritized Author Improvement Roadmap for camera-ready acceptance.

Return a JSON object with EXACTLY the following structure:
{
    "reproducibility_score": 75,
    "verdict": "Revision Required",
    "final_verdict": "Revision Required",
    "verdict_rationale": "2-3 sentences explaining final recommendation",
    "reconciliation_summary": "Synthesized reconciliation explaining how Skeptic and Critic findings align or conflict",
    "reconciliation_debate_summary": "Synthesized reconciliation explaining how Skeptic and Critic findings align or conflict",
    "debate_trace": [
        {"step": 1, "speaker": "Agent 1 (The Skeptic)", "point": "Methodological ambiguity or assumption raised"},
        {"step": 2, "speaker": "Agent 2 (The Critic)", "point": "Statistical flaw, sample size issue, or formula anomaly noted"},
        {"step": 3, "speaker": "Agent 3 (Lead Arbiter)", "point": "Consensus verdict and reconciliation resolution"}
    ],
    "claims_matrix": [
        {
            "claim_id": "C1",
            "claim_text": "Extracted claim from paper",
            "verdict_type": "Supported & Verifiable",
            "evidence_note": "Detailed justification of evidence match or gap"
        }
    ],
    "claim_matrix": [
        {
            "claim_id": "C1",
            "claim_text": "Extracted claim from paper",
            "verdict_type": "Supported & Verifiable",
            "evidence_note": "Detailed justification of evidence match or gap"
        }
    ],
    "component_scores": {
        "methodology_rigor": 75,
        "statistical_integrity": 70,
        "empirical_replicability": 80,
        "data_transparency": 70,
        "theoretical_soundness": 75
    },
    "peer_review_matrix": {
        "strengths": [
            {"category": "Formulation", "point": "Clear problem statement"}
        ],
        "critical_flaws": [
            {"category": "Statistical", "issue": "Missing variance bounds", "impact": "Moderate"}
        ],
        "research_gaps": [
            {"area": "Ablation", "gap_description": "Lacks baseline comparison"}
        ]
    },
    "roadmap": [
        {
            "step_number": 1,
            "priority": "High",
            "target_section": "Methodology",
            "action": "Actionable technical requirement for authors",
            "expected_impact": "Impact on paper acceptance & reproducibility"
        },
        {
            "step_number": 2,
            "priority": "High",
            "target_section": "Experiments",
            "action": "Actionable step 2",
            "expected_impact": "Impact 2"
        },
        {
            "step_number": 3,
            "priority": "Medium",
            "target_section": "Statistical Disclosures",
            "action": "Actionable step 3",
            "expected_impact": "Impact 3"
        },
        {
            "step_number": 4,
            "priority": "Medium",
            "target_section": "Appendix",
            "action": "Actionable step 4",
            "expected_impact": "Impact 4"
        },
        {
            "step_number": 5,
            "priority": "Low",
            "target_section": "Code Repository",
            "action": "Actionable step 5",
            "expected_impact": "Impact 5"
        }
    ],
    "author_roadmap": [
        {
            "step_number": 1,
            "priority": "High",
            "target_section": "Methodology",
            "action": "Actionable technical requirement for authors",
            "expected_impact": "Impact on paper acceptance & reproducibility"
        }
    ]
}

Respond ONLY with valid, raw JSON (no markdown wrapping, no commentary).
"""


def run_arbiter_agent(state: ReviewState) -> Dict[str, Any]:
    """
    Node executor for Lead Arbiter & Consensus Synthesizer.
    """
    methodology_review = state.get("methodology_review", {})
    statistical_review = state.get("statistical_review", {})
    api_key = state.get("api_key") or os.getenv("GOOGLE_API_KEY")
    model_name = state.get("model_name", "gemini-1.5-flash")
    
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        
    t0 = datetime.datetime.now().strftime("%H:%M:%S")
    logs = [f"[{t0}] ⚖️ Agent 3 (Lead Arbiter): Synthesizing Skeptic & Critic reports into debate trace and author roadmap using model '{model_name}'..."]
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.1,
            model_kwargs={"response_mime_type": "application/json"}
        )
        
        input_payload = {
            "methodology_inspector_report": methodology_review,
            "statistical_auditor_report": statistical_review
        }
        
        messages = [
            SystemMessage(content=ARBITER_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=f"AGENT FINDINGS PAYLOAD:\n\n{json.dumps(input_payload, indent=2)}")
        ]
        
        response = llm.invoke(messages)
        content = response.content.strip()
        
        # Clean and parse JSON cleanly with heuristic regex fallback
        result = clean_and_parse_json(content, default_score=75)
        
        m_score = int(methodology_review.get("overall_methodology_score", 70))
        s_score = int(statistical_review.get("overall_statistical_score", 70))
        calculated_avg = round((m_score + s_score) / 2)
        
        raw_score = result.get("reproducibility_score", result.get("overall_score", calculated_avg))
        try:
            score = int(raw_score)
            score = max(0, min(100, score))
        except (ValueError, TypeError):
            score = calculated_avg
            
        result["reproducibility_score"] = score
        
        # Ensure Component Scores
        comp_scores = result.get("component_scores", {})
        cleaned_comp = {}
        for key in ["methodology_rigor", "statistical_integrity", "empirical_replicability", "data_transparency", "theoretical_soundness"]:
            val = comp_scores.get(key, score)
            try:
                c_val = int(val)
                c_val = max(0, min(100, c_val))
            except (ValueError, TypeError):
                c_val = score
            cleaned_comp[key] = c_val
        result["component_scores"] = cleaned_comp
        
        # If score is still 0, compute arithmetic mean of non-zero sub-scores
        if score == 0:
            vals = [v for v in cleaned_comp.values() if v > 0]
            score = round(sum(vals) / len(vals)) if vals else calculated_avg
            result["reproducibility_score"] = score
            
        # Ensure Verdict string is populated cleanly across keys
        verdict_str = result.get("verdict") or result.get("final_verdict") or result.get("recommendation") or "Revision Required"
        result["verdict"] = verdict_str
        result["final_verdict"] = verdict_str
        
        # Sync summary keys
        summary_str = result.get("reconciliation_summary") or result.get("reconciliation_debate_summary") or "Debate reconciliation complete."
        result["reconciliation_summary"] = summary_str
        result["reconciliation_debate_summary"] = summary_str
        
        # Extract v2.0 Data Structures with aliases
        debate_trace = result.get("debate_trace", [])
        claims_matrix = result.get("claims_matrix") or result.get("claim_matrix") or []
        result["claims_matrix"] = claims_matrix
        result["claim_matrix"] = claims_matrix
        
        roadmap = result.get("roadmap") or result.get("author_roadmap") or result.get("author_action_plan") or []
        result["roadmap"] = roadmap
        result["author_roadmap"] = roadmap
        
        t_done = datetime.datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{t_done}] 🟢 Agent 3 (Lead Arbiter): Consensus achieved! Reproducibility Score: {score}/100. Verdict: {verdict_str}.")
        
        return {
            "arbiter_review": result,
            "final_verdict": result,
            "debate_trace": debate_trace,
            "claim_matrix": claims_matrix,
            "author_roadmap": roadmap,
            "thought_logs": logs,
            "status": "completed"
        }
        
    except Exception as e:
        print("[Agent 3 Error Traceback]:")
        traceback.print_exc()
        t_err = datetime.datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{t_err}] 🔴 Agent 3 (Lead Arbiter): Exception during synthesis: {type(e).__name__} - {str(e)}")
        
        m_score = int(methodology_review.get("overall_methodology_score", 65))
        s_score = int(statistical_review.get("overall_statistical_score", 65))
        avg_score = round((m_score + s_score) / 2)
        
        fallback_res = clean_and_parse_json("", default_score=avg_score)
        fallback_res["reproducibility_score"] = avg_score
        fallback_res["verdict"] = "Revision Required"
        fallback_res["final_verdict"] = "Revision Required"
        fallback_res["error"] = str(e)
        
        return {
            "arbiter_review": fallback_res,
            "final_verdict": fallback_res,
            "debate_trace": fallback_res.get("debate_trace", []),
            "claim_matrix": fallback_res.get("claim_matrix", []),
            "author_roadmap": fallback_res.get("author_action_plan", []),
            "thought_logs": logs,
            "status": "completed_with_fallback"
        }
