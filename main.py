# main.py
"""
Main entry point: Run multi-agent system with 5 test queries.

Query Types:
1. Theory/Conceptual - "Explain ReAct pattern..."
2. Design/Architecture - "Design multi-agent system..."
3. Code/Implementation - "Write LRU cache..."
4. Planning - "Create 3-week learning plan..."
5. Memory Test - Query then follow-up (tests conversation memory)
"""

import os
import json
from typing import Dict, List
from src.models import GraphState, SessionMemory
from src.graph import build_graph


# ============================================================================
# Test Queries
# ============================================================================

TEST_QUERIES = [
    {
        "id": 1,
        "type": "theory",
        "query": "Explain the ReAct pattern in multi-agent systems. What are its key components?",
        "expected_agent": "theory_explainer"
    },
    {
        "id": 2,
        "type": "design",
        "query": "Design a scalable microservices architecture for a real-time chat application.",
        "expected_agent": "design_advisor"
    },
    {
        "id": 3,
        "type": "code",
        "query": "Write Python code to implement an LRU Cache with O(1) lookup, insert, and delete.",
        "expected_agent": "code_helper"
    },
    {
        "id": 4,
        "type": "planning",
        "query": "Create a 3-week learning plan to master LangChain and LangGraph for building AI agents.",
        "expected_agent": "planner"
    },
    {
        "id": 5,
        "type": "memory_test",
        "query": "What is ReAct? (First query to populate memory)",
        "expected_agent": "theory_explainer"
    }
]


# ============================================================================
# Result Recording
# ============================================================================

class ResultRecorder:
    """Records experiment results in structured format."""
    
    def __init__(self):
        self.results = []
    
    def record(self, query_id: int, query: str, final_state: Dict) -> Dict:
        """Record single query result."""
        result = {
            "query_id": query_id,
            "query": query[:80],
            "routing": "unknown",
            "agents_used": [],
            "tools_used": [],
            "memory_read": [],
            "memory_write": [],
            "quality": "N/A",
            "time": "N/A",
            "errors": final_state.get("errors", [])
        }
        
        # Extract execution info
        if final_state.get("classification"):
            result["routing"] = final_state["classification"].query_type
            result["agents_used"] = final_state["classification"].agent_path
        
        if final_state.get("agent_outputs"):
            result["agents_used"] = list(final_state["agent_outputs"].keys())
            # Capture full agent outputs
            result["agent_outputs"] = {k: str(v) for k, v in final_state["agent_outputs"].items()}

        # Capture final answer and full query
        result["full_query"] = query
        final_ans = final_state.get("final_answer")
        if final_ans:
             # Use model_dump for Pydantic v2, fallback to dict for v1
            result["final_answer"] = (
                final_ans.model_dump() if hasattr(final_ans, "model_dump") 
                else final_ans.dict() if hasattr(final_ans, "dict") 
                else str(final_ans)
            )
        else:
            result["final_answer"] = None
        
        # Memory info
        memory = final_state.get("session_memory")
        if memory:
            result["memory_read"] = memory.previous_questions[-2:] if len(memory.previous_questions) > 1 else []
            result["memory_write"] = ["conversation_history", "previous_questions"]
        
        self.results.append(result)
        return result
    
    def to_markdown(self) -> str:
        """Convert results to markdown table."""
        md = "\n## Experiment Results\n\n"
        md += "| Query | Type | Agents | Tools | Memory | Quality |\n"
        md += "|-------|------|--------|-------|--------|----------|\n"
        
        for r in self.results:
            agents_str = " -> ".join(r["agents_used"]) if r["agents_used"] else "N/A"
            tools_str = ", ".join(r["tools_used"]) if r["tools_used"] else "-"
            memory_str = "" if r["memory_write"] else "-"
            quality_str = "****" if not r["errors"] else "!"
            
            md += "| {} | {} | {} | {} | {} | {} |\n".format(
                r["query_id"],
                r["routing"],
                agents_str,
                tools_str,
                memory_str,
                quality_str
            )
        
        return md


# ============================================================================
# Main Execution
# ============================================================================

def run_assistant(query: str, session_id: str = "default") -> Dict:
    """
    Execute single query through the multi-agent system.
    
    Args:
        query: User question
        session_id: Session identifier for memory
        
    Returns:
        Final state from LangGraph execution
    """
    print("\n" + "="*80)
    print("QUERY: {}".format(query))
    print("="*80)
    
    initial_state = GraphState(
        user_query=query,
        session_memory=SessionMemory(session_id=session_id),
        classification=None,
        react_chain=[],
        agent_outputs={},
        final_answer=None,
        execution_log=[],
        errors=[],
        retry_count=0
    )
    
    try:
        graph = build_graph()
        final_state = graph.invoke(initial_state)
    except Exception as e:
        print("\nERROR: {}".format(e))
        return {"error": str(e), "errors": [str(e)]}
    
    # Print summary
    print("\n" + "="*80)
    print("EXECUTION SUMMARY")
    print("="*80)
    
    if final_state.get("classification"):
        print("\nQuery Type: {}".format(final_state["classification"].query_type))
        print("Agent Path: {}".format(" -> ".join(final_state["classification"].agent_path)))
    
    print("\nReAct Chain ({} steps):".format(len(final_state.get("react_chain", []))))
    print("\nReAct Chain ({} steps):".format(len(final_state.get("react_chain", []))))
    for i, thought in enumerate(final_state.get("react_chain", []), 1):
        print("\n  {}. THOUGHT: {}".format(i, thought.thought.replace("\u2192", "->")))
        print("     ACTION:  {}".format(thought.action.replace("\u2192", "->")))
        if thought.observation:
            print("     OBSERV:  {}".format(thought.observation[:60].replace("\u2192", "->")))
    
    if final_state.get("agent_outputs"):
        print("\n\nAgent Outputs:")
        for agent_name, output in final_state["agent_outputs"].items():
            if hasattr(output, '__dict__'):
                print("  - {}: {}...".format(agent_name, str(output)[:100]))
    
    if final_state.get("errors"):
        print("\n\nErrors:")
        for error in final_state.get("errors", [])[:2]:
            print("  - {}".format(error[:100]))
    
    print("\nExecution Log: {}".format(" -> ".join(final_state.get("execution_log", []))))
    print("="*80)
    
    return final_state


def main():
    """Run all test queries and record results."""
    print("\n" + "="*80)
    print("MULTI-AGENT SYSTEM EVALUATION")
    print("="*80)
    print("\nRunning {} test queries...\n".format(len(TEST_QUERIES)))
    
    recorder = ResultRecorder()
    session_id = "lab2_session"
    
    # Run each query
    for test_case in TEST_QUERIES:
        query_id = test_case["id"]
        query = test_case["query"]
        
        print("\n>>> QUERY {}: [{}]".format(query_id, test_case["type"].upper()))
        
        final_state = run_assistant(query, session_id=session_id)
        recorder.record(query_id, query, final_state)
    
    # Print results table
    print("\n\n" + "="*80)
    print(recorder.to_markdown())
    print("="*80)
    
    # Save results to JSON
    results_file = "experiment_results.json"
    with open(results_file, "w") as f:
        json.dump(
            {
                "total_queries": len(TEST_QUERIES),
                "results": recorder.results
            },
            f,
            indent=2
        )
    print(" Results saved to {}".format(results_file))


if __name__ == "__main__":
    main()