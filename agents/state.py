"""
Shared State Schema for MetaReviewer-AI v2.0 Multi-Agent Graph Workflow.
Uses Annotated[List[str], operator.add] to handle state logging updates safely across nodes.
"""

import operator
from typing import Annotated, TypedDict, List, Dict, Any, Optional

class ReviewState(TypedDict, total=False):
    paper_text: str
    paper_title: str
    api_key: Optional[str]
    model_name: str
    
    # Live execution logs
    thought_logs: Annotated[List[str], operator.add]
    
    # Core Agent Reviews
    methodology_review: Dict[str, Any]
    statistical_review: Dict[str, Any]
    arbiter_review: Dict[str, Any]
    final_verdict: Dict[str, Any]
    
    # v2.0 Upgraded Features
    claim_matrix: List[Dict[str, Any]]       # Claim-by-Claim Verification Matrix
    debate_trace: List[Dict[str, Any]]       # Interactive Multi-Agent Debate Trace
    author_roadmap: List[Dict[str, Any]]     # 5-Step Author Improvement Roadmap
    
    status: str
    error: Optional[str]
