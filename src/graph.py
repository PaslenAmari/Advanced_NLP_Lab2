# graph.py
"""
LangGraph Setup: Build the multi-agent state graph.

Graph structure:
    START → Router → [Specialist] → Synthesizer → END
    
Where [Specialist] is one of:
- theory_explainer
- design_advisor
- code_helper
- planner

Routing is conditional based on query classification.
"""

from langgraph.graph import StateGraph, START, END
from .models import GraphState
from .agents import (
    router_node,
    theory_explainer_node,
    design_advisor_node,
    code_helper_node,
    planner_node,
    memory_retriever_node,
    synthesizer_node,
    route_to_agents,
)


def build_graph():
    """
    Build the LangGraph state machine.
    
    Nodes:
    - router: Classifies query
    - theory_explainer: Theory/conceptual queries
    - design_advisor: Architecture/design queries
    - code_helper: Programming/code queries
    - planner: Planning/organization queries
    - synthesizer: Final answer assembly
    
    Edges:
    - START → router
    - router → [conditional routing to specialist]
    - [all specialists] → synthesizer
    - synthesizer → END
    
    Returns:
        Compiled LangGraph
    """
    print("Building LangGraph...")
    
    # Create state graph
    graph = StateGraph(GraphState)
    
    # ========== ADD NODES ==========
    graph.add_node("router", router_node)
    graph.add_node("memory_retriever", memory_retriever_node)
    graph.add_node("theory_explainer", theory_explainer_node)
    graph.add_node("design_advisor", design_advisor_node)
    graph.add_node("code_helper", code_helper_node)
    graph.add_node("planner", planner_node)
    graph.add_node("synthesizer", synthesizer_node)
    
    # ========== ADD EDGES ==========
    
    # Entry point: START → router
    graph.add_edge(START, "router")
    
    # Conditional routing: router → specialist based on query_type
    graph.add_conditional_edges(
        "router",
        route_to_agents,
        {
            "theory_explainer": "memory_retriever",
            "design_advisor": "memory_retriever",
            "code_helper": "memory_retriever",
            "planner": "memory_retriever",
            "synthesizer": "synthesizer",  # If no classification
        }
    )
    
    # After memory retrieval, route to the ACTUAL specialist
    def route_after_memory(state: GraphState) -> str:
        return route_to_agents(state)

    graph.add_conditional_edges(
        "memory_retriever",
        route_after_memory,
        {
            "theory_explainer": "theory_explainer",
            "design_advisor": "design_advisor",
            "code_helper": "code_helper",
            "planner": "planner",
            "synthesizer": "synthesizer",
        }
    )
    
    # All specialists lead to synthesizer
    for agent in ["theory_explainer", "design_advisor", "code_helper", "planner"]:
        graph.add_edge(agent, "synthesizer")
    
    # Synthesizer is the final step
    graph.add_edge("synthesizer", END)
    
    print(" Graph built with 6 nodes and conditional routing")
    return graph.compile()


if __name__ == "__main__":    
    print("\n" + "="*80)
    print("VISUALIZING SYSTEM ARCHITECTURE")
    print("="*80)
    
    try:
        graph = build_graph()        
        
        print("\nGenerating Mermaid code...")
        mermaid_code = graph.get_graph().draw_mermaid()        
        
        with open("lab2_architecture.mmd", "w") as f:
            f.write(mermaid_code)        
        
        print("\n" + "="*80)
        print("MERMAID DIAGRAM:")
        print("="*80)
        print(mermaid_code)
        print("="*80)
        
        print("\n Saved to: lab2_architecture.mmd")
        print("\n To convert to PNG:")
        print("   Visit: https://mermaid.live/")
        print("   Paste the code above and download")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()