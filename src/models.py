# models.py
"""
Data models and Pydantic schemas for the Multi-Agent System.
TypedDicts for state, Pydantic models for structured outputs.
"""

from typing import TypedDict, Optional, List, Dict, Any
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


# ============================================================================
# Pydantic Models - Structured Outputs
# ============================================================================

class QueryClassification(BaseModel):
    """Router output: classifies the user query into one of 4 types."""
    query_type: str = Field(..., description="theory|design|code|planning")
    complexity: str = Field(default="medium", description="simple|medium|complex")
    requires_tools: bool = Field(default=False)
    agent_path: List[str] = Field(..., description="List of agent names in the route")
    reasoning: str = Field(..., description="Why this classification?")


class TheoryExplanation(BaseModel):
    """Theory Explainer Agent output."""
    topic: str = Field(...)
    explanation: str = Field(...)
    key_concepts: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0, le=1)


class DesignAdvice(BaseModel):
    """Design Advisor Agent output."""
    design_patterns: List[str] = Field(...)
    architecture_recommendation: str = Field(...)
    pros_cons: Dict[str, List[str]] = Field(...)
    code_snippet: Optional[str] = Field(default=None)


class CodeSolution(BaseModel):
    """Code Helper Agent output."""
    problem: str = Field(...)
    solution_explanation: str = Field(...)
    code: str = Field(...)
    complexity: str = Field(default="O(n)")
    test_cases: List[Dict[str, str]] = Field(default_factory=list)


class PlanOutput(BaseModel):
    """Planner Agent output."""
    goal: str = Field(...)
    steps: List[Dict[str, str]] = Field(...)
    timeline: str = Field(...)
    resources_needed: List[str] = Field(default_factory=list)


class ReActThought(BaseModel):
    """Single step in ReAct chain: Thought → Action → Observation."""
    thought: str = Field(...)
    action: str = Field(...)
    observation: Optional[str] = Field(default=None)


class AgentResponse(BaseModel):
    """Final response from an agent or synthesizer."""
    react_thoughts: List[ReActThought] = Field(...)
    final_answer: str = Field(...)
    source_agent: str = Field(...)
    used_tools: List[str] = Field(default_factory=list)


# ============================================================================
# Session Memory - Dataclass for persistence
# ============================================================================

@dataclass
class SessionMemory:
    """Persistent memory for a conversation session."""
    session_id: str = "default"
    user_profile: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    previous_questions: List[str] = field(default_factory=list)
    learned_topics: List[str] = field(default_factory=list)


# ============================================================================
# LangGraph State - TypedDict for graph state
# ============================================================================

class GraphState(TypedDict, total=False):
    """
    State object passed through the LangGraph.
    Each node can read and modify this state.
    """
    user_query: str
    session_memory: SessionMemory
    classification: Optional[QueryClassification]
    react_chain: List[ReActThought]
    agent_outputs: Dict[str, Any]
    final_answer: Optional[AgentResponse]
    execution_log: List[str]
    errors: List[str]
    retry_count: int