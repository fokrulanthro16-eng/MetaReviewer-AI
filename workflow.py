"""
LangGraph Workflow Compiler for MetaReviewer-AI v2.0.
Assembles the multi-agent graph with sequential node flow:
START -> methodology_inspector -> statistical_auditor -> lead_arbiter -> END
"""

import datetime
from langgraph.graph import StateGraph, START, END
from agents.state import ReviewState
from agents.methodology_agent import run_methodology_agent
from agents.statistical_agent import run_statistical_agent
from agents.arbiter_agent import run_arbiter_agent


def initialize_workflow_state(paper_text: str, paper_title: str = "Research Paper", api_key: str = None, model_name: str = "gemini-1.5-flash") -> ReviewState:
    """
    Creates initial state for the MetaReviewer-AI v2.0 LangGraph workflow.
    """
    t0 = datetime.datetime.now().strftime("%H:%M:%S")
    initial_log = f"[{t0}] 🟡 System Orchestrator: Initialized MetaReviewer-AI v2.0 graph for '{paper_title}' (Model: {model_name})."
    
    return ReviewState(
        paper_title=paper_title,
        paper_text=paper_text,
        api_key=api_key,
        model_name=model_name,
        methodology_review={},
        statistical_review={},
        arbiter_review={},
        final_verdict={},
        claim_matrix=[],
        debate_trace=[],
        author_roadmap=[],
        thought_logs=[initial_log],
        status="started",
        error=None
    )


def build_meta_reviewer_graph():
    """
    Compiles the LangGraph StateGraph for MetaReviewer-AI v2.0.
    Sequential Execution Pipeline:
    START ---> methodology_inspector ---> statistical_auditor ---> lead_arbiter ---> END
    """
    builder = StateGraph(ReviewState)
    
    # Add Agent Nodes
    builder.add_node("methodology_inspector", run_methodology_agent)
    builder.add_node("statistical_auditor", run_statistical_agent)
    builder.add_node("lead_arbiter", run_arbiter_agent)
    
    # Define Sequential Edges
    builder.add_edge(START, "methodology_inspector")
    builder.add_edge("methodology_inspector", "statistical_auditor")
    builder.add_edge("statistical_auditor", "lead_arbiter")
    builder.add_edge("lead_arbiter", END)
    
    return builder.compile()


# Compiled Singleton Graph Instance
meta_reviewer_graph = build_meta_reviewer_graph()


def run_meta_reviewer(paper_text: str, paper_title: str = "Research Paper", api_key: str = None, model_name: str = "gemini-1.5-flash") -> ReviewState:
    """
    Executes the entire multi-agent review graph synchronously and returns the final state.
    """
    initial_state = initialize_workflow_state(
        paper_text=paper_text,
        paper_title=paper_title,
        api_key=api_key,
        model_name=model_name
    )
    
    final_state = meta_reviewer_graph.invoke(initial_state)
    return final_state
