#!/usr/bin/env python
"""
system data structures inspector and monitor
shows where stored are:
- queries
- responses
- logs
- cache
- session memory
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src import build_graph, SessionMemory
from src.cache import get_cache, get_deduplicator


def print_section(title: str, char: str = "=", width: int = 80):
    """print formatted section header"""
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}\n")


def inspect_session_memory():
    """inspect SessionMemory data structure"""
    print_section("SESSION MEMORY STRUCTURE", "─")
    
    session = SessionMemory(session_id="inspection")
    
    print(" SessionMemory attributes:")
    print(f"  session_id: {session.session_id}")
    print(f"  created_at: {session.created_at}")
    print(f"  conversations: {session.conversations}")
    print(f"  retrieved_documents: {session.retrieved_documents}")
    print(f"  execution_history: {session.execution_history}")
    
    print("\n SessionMemory methods:")
    print("  • read(query_type): read from memory")
    print("  • write(query_type, value): write to memory")
    print("  • add_to_conversation(role, content): add message")
    print("  • retrieve_documents(query): get docs")
    print("  • log_execution(agent, input, output): log action")
    
    print("\n Data Storage:")
    print("  └─ conversations: Dict[str, List[Dict]]")
    print("     └─ keys: 'theory', 'design', 'code', 'planning'")
    print("        └─ values: [{'role': 'user'/'assistant', 'content': str}]")
    print("  └─ retrieved_documents: List[str]")
    print("  └─ execution_history: List[Dict]")
    print("     └─ {'agent': str, 'input': str, 'output': str, 'timestamp': str}")


def inspect_cache_structure():
    """inspect QueryCache data structure"""
    print_section("QUERY CACHE STRUCTURE", "─")
    
    cache = get_cache()
    dedup = get_deduplicator()
    
    print(" QueryCache attributes:")
    print(f"  max_size: {cache.max_size}")
    print(f"  ttl: {cache.ttl}")
    print(f"  cache: Dict[str, Dict] (hash → entry)")
    
    print("\n Cache Entry Format:")
    print("""
    {
        'query': str,                    # original query text
        'result': Dict,                  # execution result
        'execution_time': float,         # time taken (seconds)
        'timestamp': datetime,           # when cached
        'expires': datetime             # TTL expiration
    }
    """)
    
    print(" Cache Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print("\n RequestDeduplicator attributes:")
    print(f"  threshold: {dedup.threshold}")
    print(f"  processed_queries: Dict[str, Dict]")
    print(f"  - stores: query_text → result")
    
    print("\n How it works:")
    print("  1. New query arrives")
    print("  2. Hash query with MD5")
    print("  3. Check if hash exists in cache")
    print("  4. If not found, check similarity with RequestDeduplicator")
    print("  5. If similar (threshold match), reuse result")
    print("  6. Otherwise, execute and cache")


def inspect_react_chain_structure():
    """inspect ReAct pattern chain structure"""
    print_section("ReAct CHAIN STRUCTURE", "─")
    
    print(" ReAct Chain (Reasoning and Acting):")
    print("""
    react_chain: List[Dict]
    
    Each step in chain contains:
    {
        'step': int,                      # step number (1, 2, 3, ...)
        'thought': str,                   # agent's reasoning
        'action': str,                    # what agent decided to do
        'observation': str,               # result of action
        'agent': str,                     # which agent executed
        'timestamp': str                  # when executed
    }
    """)
    
    print(" Example ReAct Chain (3 steps):")
    print("""
    STEP 1 (Router):
      THOUGHT: "User asks about machine learning - this is theory"
      ACTION: "Classify as theory type"
      OBSERVATION: "Type=theory, Complexity=simple, Route=theory_agent"
    
    STEP 2 (Theory Agent):
      THOUGHT: "Explaining machine learning fundamentals"
      ACTION: "Call LLM for explanation"
      OBSERVATION: "Machine learning is a subset of AI that..."
    
    STEP 3 (Synthesizer):
      THOUGHT: "Combining router and theory results"
      ACTION: "Create final answer"
      OBSERVATION: "Final comprehensive answer ready"
    """)


def inspect_graph_state_structure():
    """inspect LangGraph GraphState structure"""
    print_section("LANGGRAPH STATE STRUCTURE", "─")
    
    print(" GraphState TypedDict:")
    print("""
    {
        'user_query': str,                # user's original question
        'session_memory': SessionMemory,  # context + history
        'classification': QueryClassification,  # routing decision
        'react_chain': List[Dict],        # all reasoning steps
        'agent_outputs': Dict[str, str],  # {agent_name: response}
        'final_answer': str,              # synthesized answer
        'execution_log': List[str],       # step-by-step logs
        'errors': List[str],              # any errors
        'retry_count': int                # retry attempts
    }
    """)
    
    print(" Graph Nodes:")
    print("""
    1. ROUTER
       ├─ Input: user_query, session_memory
       ├─ Process: Classify query type with ReAct
       └─ Output: classification, react_chain update
    
    2. THEORY AGENT
       ├─ Input: user_query, session_memory
       ├─ Process: Explain concepts
       └─ Output: agent_outputs['theory']
    
    3. DESIGN AGENT
       ├─ Input: user_query, session_memory
       ├─ Process: Architecture advice
       └─ Output: agent_outputs['design']
    
    4. CODE AGENT
       ├─ Input: user_query, session_memory
       ├─ Process: Generate code
       └─ Output: agent_outputs['code']
    
    5. PLAN AGENT
       ├─ Input: user_query, session_memory
       ├─ Process: Create learning plan
       └─ Output: agent_outputs['plan']
    
    6. SYNTHESIZER
       ├─ Input: all previous outputs
       ├─ Process: Combine and format
       └─ Output: final_answer, execution_log
    """)


def inspect_file_structure():
    """show file and directory structure"""
    print_section("FILE STRUCTURE", "─")
    
    print(" Project Layout:")
    print("""
    ADVANCED_NLP_LAB2/
    │
    ├──  main.py                 ← Entry point (run experiments)
    ├──  test_caching.py         ← Cache tests
    ├──  test_custom.py          ← Custom query tests
    ├──  ARCHITECTURE.md         ← Design document
    ├──  README.md               ← Overview
    ├──  experiment_results.json ← Results from main.py
    │
    ├──  src/                    ← Source code
    │   ├── __init__.py            ← Export: build_graph, SessionMemory
    │   ├── models.py              ← Pydantic models (QueryClassification, etc)
    │   ├── agents.py              ← 5 agents (theory, design, code, plan, synthesizer)
    │   ├── graph.py               ← LangGraph setup (6 nodes)
    │   ├── memory.py              ← SessionMemory class
    │   ├── cache.py               ← QueryCache + RequestDeduplicator
    │   ├── config.py              ← LLM config
    │   ├── tools.py               ← Tool definitions
    │   └── utils.py               ← Helper functions
    │
    ├──  tests/                  ← Tests
    │   ├── test_caching.py        ← Cache functionality
    │   └── test_imports.py        ← Import tests
    │
    └──  data/                   ← Data files
        └── (empty - ready for data)
    """)
    
    print("\n Data Storage Locations:")
    print("""
    1. SESSION MEMORY (Runtime, In-Memory)
       └─ Location: src/memory.py (SessionMemory class)
       └─ Stores: conversation history, retrieved docs, execution history
       └─ Lifecycle: Created per session, destroyed after session
       └─ Access: session.read(query_type), session.write(query_type, value)
    
    2. QUERY CACHE (Runtime, In-Memory)
       └─ Location: src/cache.py (QueryCache class)
       └─ Stores: query results with TTL expiration
       └─ Lifecycle: Lives entire process, cleared on exit
       └─ Access: cache.get(query), cache.put(query, result, time)
    
    3. EXECUTION LOG (Runtime, In-Memory)
       └─ Location: GraphState.execution_log (List[str])
       └─ Stores: step-by-step execution trace
       └─ Access: printed to console during execution
    
    4. REACT CHAIN (Runtime, In-Memory)
       └─ Location: GraphState.react_chain (List[Dict])
       └─ Stores: thought → action → observation steps
       └─ Access: visible in console output
    
    5. EXPERIMENT RESULTS (Persistent, JSON)
       └─ Location: experiment_results.json
       └─ Stores: query results, routing decisions, timings
       └─ Access: JSON format, can be read/analyzed
    """)


def inspect_data_flow():
    """show data flow through system"""
    print_section("DATA FLOW", "─")
    
    print(" Request → Response Flow:")
    print("""
    USER QUERY
         ↓
    [1] CACHE CHECK (QueryCache.get)
         ├─ Hit? → Return cached result
         └─ Miss? → Continue
              ↓
    [2] DEDUPLICATION CHECK (RequestDeduplicator.find_duplicate)
         ├─ Similar query found? → Reuse result
         └─ New query? → Continue
              ↓
    [3] ROUTER NODE
         ├─ Classify: theory/design/code/planning
         ├─ Update: react_chain, classification
         └─ Route to appropriate agent
              ↓
    [4] SPECIALIZED AGENT (theory/design/code/plan)
         ├─ Retrieve: session memory context
         ├─ Execute: ReAct pattern
         ├─ Update: agent_outputs, react_chain
         └─ Pass to synthesizer
              ↓
    [5] SYNTHESIZER NODE
         ├─ Combine: all agent outputs
         ├─ Format: final answer
         ├─ Update: execution_log, final_answer
         └─ Return result
              ↓
    [6] CACHING
         ├─ Store: result in QueryCache
         ├─ Register: in RequestDeduplicator
         └─ Update: session memory history
              ↓
    FINAL ANSWER
    """)


def create_data_visualization():
    """create visualization of data structures"""
    print_section("DATA VISUALIZATION", "─")
    
    print(" Memory Hierarchy:")
    print("""
    PROCESS MEMORY
    ├── SessionMemory
    │   ├── conversations: {
    │   │   "theory": [{role, content}, ...],
    │   │   "design": [{role, content}, ...],
    │   │   ...
    │   ├── retrieved_documents: [doc1, doc2, ...]
    │   └── execution_history: [{agent, input, output}, ...]
    │
    ├── QueryCache
    │   ├── cache: {
    │   │   "hash1": {query, result, time, expires},
    │   │   "hash2": {query, result, time, expires},
    │   │   ...
    │   └── stats: {hits, misses, hit_rate, time_saved}
    │
    ├── RequestDeduplicator
    │   └── processed_queries: {
    │       "query1": result1,
    │       "query2": result2,
    │       ...
    │
    └── GraphState
        ├── react_chain: [{step, thought, action, observation}, ...]
        ├── agent_outputs: {theory: "...", design: "...", ...}
        ├── execution_log: ["step1", "step2", ...]
        └── final_answer: "..."
    """)


def main():
    """main inspection function"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  ADVANCED NLP LAB 2 - DATA STRUCTURES & STORAGE INSPECTION".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Run inspections
    inspect_session_memory()
    inspect_cache_structure()
    inspect_react_chain_structure()
    inspect_graph_state_structure()
    inspect_file_structure()
    inspect_data_flow()
    create_data_visualization()
    
    print_section("SUMMARY", "═")
    print("""
     Data Structures:
       • SessionMemory - per-session context (in-memory)
       • QueryCache - result caching with TTL (in-memory)
       • RequestDeduplicator - similarity matching (in-memory)
       • GraphState - LangGraph execution state (in-memory)
       • ReAct Chain - reasoning steps (in-memory)
    
     Queries Storage:
       • In SessionMemory.conversations (by type)
       • In RequestDeduplicator.processed_queries (for dedup)
       • In execution_log (as text)
    
     Responses Storage:
       • In QueryCache.cache (results)
       • In agent_outputs (per agent)
       • In final_answer (synthesized)
    
     Logs Storage:
       • execution_log: List[str] - step trace
       • react_chain: List[Dict] - thought/action/observation
       • Console output - realtime visibility
       • experiment_results.json - persistent results
    
     All storage is IN-MEMORY. To persist, add:
       • MongoDB/PostgreSQL for queries & responses
       • File system or S3 for logs
       • Redis for distributed cache
    """)


if __name__ == "__main__":
    main()