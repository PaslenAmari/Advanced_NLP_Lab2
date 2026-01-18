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
        "description": "Conceptual/theoretical question about MAS/LLM agents",
        "query": "Explain the difference between ReAct and Plan-and-Solve patterns in Multi-Agent Systems. Use your knowledge base tool.",
        "expected_agent": "theory_explainer"
    },
    {
        "id": 2,
        "type": "design",
        "description": "Design/architecture question",
        "query": "Design a scalable microservices architecture for a real-time analytics dashboard. Suggest patterns.",
        "expected_agent": "design_advisor"
    },
    {
        "id": 3,
        "type": "code",
        "description": "Implementation/coding question",
        "query": "Write a Python function to calculate the Fibonacci sequence up to N. Use the python executor to verify.",
        "expected_agent": "code_helper"
    },
    {
        "id": 4,
        "type": "productivity",
        "description": "Everyday tasks / productivity",
        "query": "Create a cleaning schedule for a 2-bedroom apartment for the next month. Save it to my notes.",
        "expected_agent": "planner"
    },
    {
        "id": 5,
        "type": "memory_test",
        "description": "Everyday tasks / productivity + Memory test",
        "query": "What was the cleaning schedule we just created? Summarize it.",
        "expected_agent": "planner"
    }
]


# ============================================================================
# Result Recording
# ============================================================================

class ResultRecorder:
    """Records experiment results in structured format."""
    
    def __init__(self):
        self.results = []
    
    def record(self, test_case: Dict, final_state: Dict) -> Dict:
        """Record single query result with details required by Task 3."""
        result = {
            "query_id": test_case["id"],
            "query_type": test_case["type"],
            "description": test_case.get("description", ""),
            "query": test_case["query"],
            "node_execution_order": final_state.get("execution_log", []),
            "tools_invoked": [],
            "memory_usage": {
                "read": [],
                "write": []
            },
            "useful": "Yes (Default)",
            "improvements": "None (Default)",
            "errors": final_state.get("errors", [])
        }
        
        # Capture tools from final answer or state
        final_ans = final_state.get("final_answer")
        if final_ans and hasattr(final_ans, "used_tools"):
            result["tools_invoked"] = final_ans.used_tools
            
        # Capture memory usage
        memory = final_state.get("session_memory")
        if memory:
            if len(memory.conversation_history) > 1:
                result["memory_usage"]["read"] = ["Previous history turn(s)"]
            result["memory_usage"]["write"] = ["Updated history", "Updated learned topics"]
        
        self.results.append(result)
        return result
    
    def to_markdown(self) -> str:
        """Convert results to a detailed markdown report for Task 3."""
        md = "# Task 3: Experiment Recording & Evaluation\n\n"
        
        for r in self.results:
            md += "### Experiment {}: [{}]\n".format(r["query_id"], r["query_type"].upper())
            md += "- **Description**: {}\n".format(r["description"])
            md += "- **Query**: `{}`\n".format(r["query"])
            md += "- **Node Execution Order**: {}\n".format(" → ".join(r["node_execution_order"]))
            md += "- **Tools Invoked**: {}\n".format(", ".join(r["tools_invoked"]) if r["tools_invoked"] else "None")
            md += "- **Memory Usage**: Read: {}, Write: {}\n".format(
                ", ".join(r["memory_usage"]["read"]) if r["memory_usage"]["read"] else "None",
                ", ".join(r["memory_usage"]["write"]) if r["memory_usage"]["write"] else "None"
            )
            md += "- **Usefulness**: {}\n".format(r["useful"])
            md += "- **Improvements**: {}\n".format(r["improvements"])
            if r["errors"]:
                md += "- **Errors**: {}\n".format("; ".join(r["errors"]))
            md += "\n---\n"
        
        return md


# ============================================================================
# Main Execution
# ============================================================================

def run_assistant(query: str, session_id: str = "default") -> Dict:
    """
    Execute single query through the multi-agent system.
    
    Args:
    - query: User question
    - session_id: Session identifier for memory
        
    Returns: final state from LangGraph execution
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
    
    if final_state.get("final_answer"):
        print("\n\nFinal Answer:")
        print(final_state["final_answer"].final_answer)
    
    if final_state.get("errors"):
        print("\n\nErrors:")
        for error in final_state.get("errors", [])[:2]:
            print("  - {}".format(error[:100]))
    
    print("\nExecution Log: {}".format(" -> ".join(final_state.get("execution_log", []))))
    print("="*80)
    
    # User-friendly output
    if final_state.get("final_answer"):
        print("\n" + "="*80)
        print("USER RESPONSE")
        print("="*80)
        print("Question: {}".format(query))
        print("Answer: {}".format(final_state["final_answer"].final_answer))
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
        recorder.record(test_case, final_state)
    
    # Print results report
    report_content = recorder.to_markdown()
    print("\n\n" + "="*80)
    print(report_content)
    print("="*80)
    
    # Save report to markdown file
    with open("experiments_report.md", "w") as f:
        f.write(report_content)
    
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