# agents.py
"""
Multi-Agent System

Agents:
1. router_node - Classifies query into type
2. theory_explainer_node - Explains concepts
3. design_advisor_node - Suggests architecture patterns
4. code_helper_node - Generates code solutions
5. planner_node - Creates actionable plans
6. synthesizer_node - Combines all outputs into final answer
"""

from typing import Dict, Any
from .models import (
    GraphState,
    QueryClassification,
    TheoryExplanation,
    DesignAdvice,
    CodeSolution,
    PlanOutput,
    ReActThought,
    AgentResponse,
)
from .config import get_llm_client, PydanticParserWithRetry
from langchain_core.prompts import PromptTemplate


# ============================================================================
# ROUTER AGENT - Query Classification
# ============================================================================

def router_node(state: GraphState) -> Dict:
    """
    Classifies the user query into one of 4 types: theory, design, code, planning.
    Creates first ReAct thought.
    
    Returns: Updated state with classification and first ReAct thought.
    """
    print("\n[ROUTER] Analyzing query with ReAct...")
    
    llm = get_llm_client()
    parser = PydanticParserWithRetry(QueryClassification, llm)
    
    thought = "Analyzing: '{}'".format(state['user_query'][:60])
    print("  THOUGHT: {}".format(thought))
    
    system_msg = "Classify user query into one of: theory, design, code, planning. Return JSON."
    
    user_msg = """User query: {query}

Return this JSON structure with your classification:
- query_type (theory|design|code|planning)
- complexity (simple|medium|complex)
- requires_tools (true/false)
- agent_path (list of agent names to execute)
- reasoning (explanation)"""
    
    prompt = PromptTemplate.from_template(system_msg + "\n" + user_msg)
    
    try:
        classification = parser.invoke_with_retry(prompt, {"query": state["user_query"]})
        
        print("  OBSERVATION: Type={}, Complexity={}".format(
            classification.query_type, classification.complexity))
        print("  Route: {}".format(" -> ".join(classification.agent_path)))
        
        react_thought = ReActThought(
            thought=thought,
            action="Route to {}".format(classification.query_type),
            observation="Path: {}".format(" → ".join(classification.agent_path))
        )
        
        return {
            "classification": classification,
            "react_chain": state["react_chain"] + [react_thought],
            "execution_log": state["execution_log"] + ["OK: Router"]
        }
    
    except Exception as e:
        print("  ERROR: {}".format(str(e)[:100]))
        return {
            "errors": state.get("errors", []) + ["Router: {}".format(str(e)[:80])],
            "execution_log": state["execution_log"] + ["FAILED: Router"]
        }


# ============================================================================
# THEORY EXPLAINER AGENT - Conceptual Knowledge
# ============================================================================

def theory_explainer_node(state: GraphState) -> Dict:
    """
    Explains concepts, theories, and abstract ideas.
    Uses knowledge base tool (simulated).
    
    Only activates if query_type == "theory".
    """
    print("\n[THEORY] Explaining concept...")
    
    if not state.get("classification") or state["classification"].query_type != "theory":
        return {}
    
    llm = get_llm_client()
    parser = PydanticParserWithRetry(TheoryExplanation, llm)
    
    system_msg = "You are a theory expert. Explain concepts clearly with examples. Return JSON."
    user_msg = """Topic: {query}

Provide:
- topic: The topic name
- explanation: Clear, detailed explanation
- key_concepts: List of important concepts
- examples: Practical examples
- confidence: Your confidence in the answer (0.0-1.0)"""
    
    prompt = PromptTemplate.from_template(system_msg + "\n" + user_msg)
    
    try:
        explanation = parser.invoke_with_retry(prompt, {"query": state["user_query"]})
        
        react_thought = ReActThought(
            thought="Explaining: {}".format(explanation.topic),
            action="Generate theory explanation with {} concepts".format(len(explanation.key_concepts)),
            observation="Confidence: {:.1%}".format(explanation.confidence)
        )
        
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), "theory": explanation},
            "react_chain": state["react_chain"] + [react_thought],
            "execution_log": state["execution_log"] + ["OK: Theory"]
        }
    
    except Exception as e:
        print("  ERROR: {}".format(str(e)[:100]))
        return {"errors": state.get("errors", []) + ["Theory: {}".format(str(e)[:80])]}


# ============================================================================
# DESIGN ADVISOR AGENT - Architecture & Patterns
# ============================================================================

def design_advisor_node(state: GraphState) -> Dict:
    """
    Provides software architecture advice and design patterns.
    Does NOT typically use tools (pure LLM reasoning).
    
    Only activates if query_type == "design".
    """
    print("\n[DESIGN] Analyzing architecture...")
    
    if not state.get("classification") or state["classification"].query_type != "design":
        return {}
    
    llm = get_llm_client()
    parser = PydanticParserWithRetry(DesignAdvice, llm)
    
    system_msg = "You are a software architect. Provide design patterns and recommendations. Return JSON."
    user_msg = """Design question: {query}

Provide:
- design_patterns: List of applicable patterns
- architecture_recommendation: Your recommended approach
- pros_cons: Dict with "pros" and "cons" lists
- code_snippet: Optional code example"""
    
    prompt = PromptTemplate.from_template(system_msg + "\n" + user_msg)
    
    try:
        advice = parser.invoke_with_retry(prompt, {"query": state["user_query"]})
        
        react_thought = ReActThought(
            thought="Analyzing design patterns",
            action="Generate architecture advice ({} patterns)".format(len(advice.design_patterns)),
            observation="Patterns: {}".format(", ".join(advice.design_patterns[:3]))
        )
        
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), "design": advice},
            "react_chain": state["react_chain"] + [react_thought],
            "execution_log": state["execution_log"] + ["OK: Design"]
        }
    
    except Exception as e:
        print("  ERROR: {}".format(str(e)[:100]))
        return {"errors": state.get("errors", []) + ["Design: {}".format(str(e)[:80])]}


# ============================================================================
# CODE HELPER AGENT - Code Generation
# ============================================================================

def code_helper_node(state: GraphState) -> Dict:
    """
    Generates code solutions for programming problems.
    Uses python_executor_tool (simulated).
    
    Only activates if query_type == "code".
    """
    print("\n[CODE] Generating solution...")
    
    if not state.get("classification") or state["classification"].query_type != "code":
        return {}
    
    llm = get_llm_client()
    parser = PydanticParserWithRetry(CodeSolution, llm)
    
    system_msg = "You are an expert programmer. Solve coding problems with code and tests. Return JSON."
    user_msg = """Problem: {query}

Provide:
- problem: Problem statement
- solution_explanation: Why this solution works
- code: Complete, working code
- complexity: Time complexity (e.g., O(n))
- test_cases: List of test cases with input/output"""
    
    prompt = PromptTemplate.from_template(system_msg + "\n" + user_msg)
    
    try:
        solution = parser.invoke_with_retry(prompt, {"query": state["user_query"]})
        
        react_thought = ReActThought(
            thought="Solving: {}".format(solution.problem[:50]),
            action="Generate code solution with {} test cases".format(len(solution.test_cases)),
            observation="Complexity: {}".format(solution.complexity)
        )
        
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), "code": solution},
            "react_chain": state["react_chain"] + [react_thought],
            "execution_log": state["execution_log"] + ["OK: Code"]
        }
    
    except Exception as e:
        print("  ERROR: {}".format(str(e)[:100]))
        return {"errors": state.get("errors", []) + ["Code: {}".format(str(e)[:80])]}


# ============================================================================
# PLANNER AGENT - Planning & Organization
# ============================================================================

def planner_node(state: GraphState) -> Dict:
    """
    Creates detailed, actionable plans for goals and tasks.
    Uses save_note_tool (simulated).
    
    Only activates if query_type == "planning".
    """
    print("\n[PLANNER] Creating plan...")
    
    if not state.get("classification") or state["classification"].query_type != "planning":
        return {}
    
    llm = get_llm_client()
    parser = PydanticParserWithRetry(PlanOutput, llm)
    
    system_msg = "You are a planning expert. Create detailed actionable plans. Return JSON."
    user_msg = """Request: {query}

Provide:
- goal: The main goal
- steps: List of steps (each with 'title' and 'description')
- timeline: Estimated timeline
- resources_needed: List of required resources"""
    
    prompt = PromptTemplate.from_template(system_msg + "\n" + user_msg)
    
    try:
        plan = parser.invoke_with_retry(prompt, {"query": state["user_query"]})
        
        react_thought = ReActThought(
            thought="Planning: {}".format(plan.goal),
            action="Generate detailed plan ({} steps)".format(len(plan.steps)),
            observation="Timeline: {}".format(plan.timeline)
        )
        
        return {
            "agent_outputs": {**state.get("agent_outputs", {}), "plan": plan},
            "react_chain": state["react_chain"] + [react_thought],
            "execution_log": state["execution_log"] + ["OK: Planner"]
        }
    
    except Exception as e:
        print("  ERROR: {}".format(str(e)[:100]))
        return {"errors": state.get("errors", []) + ["Planner: {}".format(str(e)[:80])]}


# ============================================================================
# SYNTHESIZER AGENT - Final Answer Assembly
# ============================================================================

def synthesizer_node(state: GraphState) -> Dict:
    """
    Combines outputs from all specialist agents into a final answer.
    Updates session memory with conversation history.
    
    Always executes last (after router + specialist).
    """
    print("\n[SYNTHESIZER] Creating final answer...")
    
    agent_outputs = state.get("agent_outputs", {})
    outputs_summary = ", ".join(agent_outputs.keys()) if agent_outputs else "none"
    
    # Format agent outputs for final answer
    agent_chain = " → ".join(state['classification'].agent_path) if state.get('classification') else "unknown"
    
    final_answer = AgentResponse(
        react_thoughts=state["react_chain"],
        final_answer="Processed by: {}. Agent outputs: {}".format(
            agent_chain,
            outputs_summary
        ),
        source_agent="synthesizer",
        used_tools=[]  
    )
    
    # Update session memory
    memory = state["session_memory"]
    memory.conversation_history.append({
        "query": state["user_query"],
        "response": final_answer.final_answer,
        "agents_used": list(agent_outputs.keys())
    })
    memory.previous_questions.append(state["user_query"])
    
    # Track learned topics from theory agent
    if "theory" in agent_outputs:
        theory_output = agent_outputs["theory"]
        if hasattr(theory_output, 'key_concepts'):
            memory.learned_topics.extend(theory_output.key_concepts)
    
    react_thought = ReActThought(
        thought="Combining all agent outputs",
        action="Synthesize final answer",
        observation="Agents: {} | Questions in session: {}".format(
            outputs_summary, len(memory.conversation_history)
        )
    )
    
    return {
        "final_answer": final_answer,
        "session_memory": memory,
        "react_chain": state["react_chain"] + [react_thought],
        "execution_log": state["execution_log"] + ["OK: Synthesizer"]
    }


# ============================================================================
# Routing Logic
# ============================================================================

def route_to_agents(state: GraphState) -> str:
    """
    Conditional routing based on query classification.
    Decides which specialist agent to execute.
    
    Returns: Node name to execute next.
    """
    if not state.get("classification"):
        return "synthesizer"
    
    query_type = state["classification"].query_type
    routing = {
        "theory": "theory_explainer",
        "design": "design_advisor",
        "code": "code_helper",
        "planning": "planner"
    }
    return routing.get(query_type, "synthesizer")