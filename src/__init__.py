"""
Multi-Agent Study Productivity Assistant

A LangChain + LangGraph implementation of a multi-agent system
with ReAct pattern for diverse query types.

Agents:
- Router: Query classification
- Theory Explainer: Conceptual knowledge
- Design Advisor: Architecture patterns
- Code Helper: Programming solutions
- Planner: Action planning
- Synthesizer: Final answer assembly
"""

# Import models
from .models import (
    GraphState,
    QueryClassification,
    TheoryExplanation,
    DesignAdvice,
    CodeSolution,
    PlanOutput,
    ReActThought,
    AgentResponse,
    SessionMemory,
)

#config with dependencies on external packages
from .config import get_llm_client, PydanticParserWithRetry

from .agents import (
    router_node,
    theory_explainer_node,
    design_advisor_node,
    code_helper_node,
    planner_node,
    synthesizer_node,
    route_to_agents,
)

# Final graph 
from .graph import build_graph

__version__ = "1.0.0"
__all__ = [
    "GraphState",
    "QueryClassification",
    "TheoryExplanation",
    "DesignAdvice",
    "CodeSolution",
    "PlanOutput",
    "ReActThought",
    "AgentResponse",
    "SessionMemory",
    "get_llm_client",
    "PydanticParserWithRetry",
    "router_node",
    "theory_explainer_node",
    "design_advisor_node",
    "code_helper_node",
    "planner_node",
    "synthesizer_node",
    "route_to_agents",
    "build_graph",
]
