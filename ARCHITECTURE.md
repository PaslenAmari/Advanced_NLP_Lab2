# ARCHITECTURE.md: Multi-Agent System Design

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Agent Descriptions](#agent-descriptions)
4. [State Management](#state-management)
5. [Execution Flow](#execution-flow)
6. [Tool Calling & Integration](#tool-calling--integration)
7. [Memory Management](#memory-management)
8. [ReAct Pattern Implementation](#react-pattern-implementation)
9. [Error Handling](#error-handling)
10. [Data Flow Diagrams](#data-flow-diagrams)

---

## System Overview

### Vision

Create a **Router + Specialists** multi-agent system that:
- Classifies user queries into 4 types (theory, design, code, planning)
- Routes to specialized agents with focused expertise
- Provides transparent reasoning via ReAct pattern
- Maintains conversation context through session memory
- Returns structured, validated outputs

### Architecture Pattern: Router → Specialists → Synthesizer

```
┌─────────────────────────────────────────────────────────┐
│                     USER QUERY                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │ ROUTER AGENT   │  ← Classifies query type
            │  (Classifier)  │     (theory|design|code|planning)
            └────────┬───────┘
                     │
        ┌────────────┼────────────┬─────────────┐
        │            │            │             │
        ▼            ▼            ▼             ▼
    ┌────────┐  ┌────────┐  ┌────────┐  ┌──────────┐
    │THEORY  │  │ DESIGN │  │  CODE  │  │ PLANNER  │
    │EXPLAIN │  │ADVISOR │  │HELPER  │  │ AGENT    │
    └────┬───┘  └────┬───┘  └────┬───┘  └────┬─────┘
         │           │           │           │
         └───────────┼───────────┼───────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │  SYNTHESIZER AGENT       │  ← Combines outputs
        │  + Memory Update         │
        └────────────┬─────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  FINAL ANSWER   │  ← With ReAct chain
            │  + Session Mem  │
            └─────────────────┘
```

---

## Architecture Patterns

### 1. **Router-Specialists Pattern**

**Purpose:** Decompose complex queries into specialized handling paths

**Implementation:**
```
Router:
  - LLM classifies query type
  - Returns QueryClassification with agent_path
  - Non-blocking: Decides path before execution

Specialists:
  - Each handles 1 query type
  - Can be enabled/disabled independently
  - Parallel execution possible (future)

Synthesizer:
  - Combines all outputs
  - Updates session memory
  - Returns final AgentResponse
```

**Benefits:**
- ✅ Separation of concerns
- ✅ Easy to add/remove agents
- ✅ Testable in isolation
- ✅ Scalable to many agents

### 2. **ReAct Pattern (Reasoning + Acting)**

**Purpose:** Make AI reasoning transparent and verifiable

**Cycle:** THOUGHT → ACTION → OBSERVATION

```python
ReActThought:
  - thought: "I need to explain X"
  - action: "Generate explanation"
  - observation: "Generated 3 concepts, confidence 0.9"
```

**Benefits:**
- ✅ Visible reasoning chain
- ✅ Easy to debug failures
- ✅ User can follow logic
- ✅ Intermediate checkpoints

### 3. **State Machine (LangGraph)**

**Purpose:** Orchestrate agent execution with explicit state transitions

**Features:**
- **Nodes:** Each agent is a node
- **Edges:** Connections between nodes
- **State:** GraphState passed through nodes
- **Routing:** Conditional edges based on state

---

## Agent Descriptions

### Agent 1: Router Agent

| Aspect | Details |
|--------|---------|
| **Purpose** | Classify user query into 4 types |
| **Input** | `user_query: str` |
| **Output** | `QueryClassification` |
| **Triggers** | Every request (always first) |
| **LLM Calls** | 1 |
| **Dependencies** | None |

**Output Structure:**
```python
QueryClassification:
  - query_type: "theory" | "design" | "code" | "planning"
  - complexity: "simple" | "medium" | "complex"
  - requires_tools: bool
  - agent_path: ["router", "theory_explainer", "synthesizer"]
  - reasoning: "This is a theoretical question about..."
```

**Example:**
```
Input: "Explain the ReAct pattern..."
Output: QueryClassification(
    query_type="theory",
    agent_path=["router", "theory_explainer", "synthesizer"],
    reasoning="Asks for explanation of concept"
)
```

### Agent 2: Theory Explainer Agent

| Aspect | Details |
|--------|---------|
| **Purpose** | Explain concepts, theories, abstract ideas |
| **Activated** | When `query_type == "theory"` |
| **Input** | Theory question |
| **Output** | `TheoryExplanation` |
| **Tools** | knowledge_base_tool (simulated) |
| **LLM Calls** | 1 |

**Output Structure:**
```python
TheoryExplanation:
  - topic: "ReAct Pattern"
  - explanation: "ReAct stands for Reasoning+Acting..."
  - key_concepts: ["Thought", "Action", "Observation"]
  - examples: ["Example 1...", "Example 2..."]
  - confidence: 0.92
```

**Use Cases:**
- Explain design patterns
- Define concepts
- Compare methodologies
- Provide background knowledge

### Agent 3: Design Advisor Agent

| Aspect | Details |
|--------|---------|
| **Purpose** | Suggest architecture & design patterns |
| **Activated** | When `query_type == "design"` |
| **Input** | Architecture question |
| **Output** | `DesignAdvice` |
| **Tools** | None (pure reasoning) |
| **LLM Calls** | 1 |

**Output Structure:**
```python
DesignAdvice:
  - design_patterns: ["MVC", "Observer", "Factory"]
  - architecture_recommendation: "Use microservices with..."
  - pros_cons: {
      "pros": ["Scalability", "Separation of concerns"],
      "cons": ["Complexity", "Network latency"]
    }
  - code_snippet: "# Example architecture..."
```

**Use Cases:**
- Design system architecture
- Choose design patterns
- Evaluate trade-offs
- Review design decisions

### Agent 4: Code Helper Agent

| Aspect | Details |
|--------|---------|
| **Purpose** | Generate code solutions |
| **Activated** | When `query_type == "code"` |
| **Input** | Programming problem |
| **Output** | `CodeSolution` |
| **Tools** | python_executor_tool (simulated) |
| **LLM Calls** | 1 |

**Output Structure:**
```python
CodeSolution:
  - problem: "Implement LRU Cache..."
  - solution_explanation: "Uses OrderedDict..."
  - code: "class LRUCache: ..."
  - complexity: "O(1) lookup, O(1) insert"
  - test_cases: [
      {"input": "capacity=2", "output": "success"}
    ]
```

**Use Cases:**
- Generate code solutions
- Implement algorithms
- Provide code snippets
- Test and validate solutions

### Agent 5: Planner Agent

| Aspect | Details |
|--------|---------|
| **Purpose** | Create actionable plans |
| **Activated** | When `query_type == "planning"` |
| **Input** | Planning request |
| **Output** | `PlanOutput` |
| **Tools** | save_note_tool (simulated) |
| **LLM Calls** | 1 |

**Output Structure:**
```python
PlanOutput:
  - goal: "Master LangChain in 3 weeks"
  - steps: [
      {"title": "Week 1: Basics", "description": "..."},
      {"title": "Week 2: Advanced", "description": "..."}
    ]
  - timeline: "3 weeks, 10 hours/week"
  - resources_needed: ["Python docs", "LangChain docs"]
```

**Use Cases:**
- Create learning plans
- Organize projects
- Schedule tasks
- Plan learning pathways

### Agent 6: Synthesizer Agent

| Aspect | Details |
|--------|---------|
| **Purpose** | Combine outputs into final answer |
| **Activated** | Always (last step) |
| **Input** | All agent outputs + ReAct chain |
| **Output** | `AgentResponse` |
| **Tools** | None |
| **LLM Calls** | 0 (pure synthesis) |

**Output Structure:**
```python
AgentResponse:
  - react_thoughts: [ReActThought, ...]
  - final_answer: "Processed by: router → theory → synthesizer"
  - source_agent: "synthesizer"
  - used_tools: ["knowledge_base_tool"]
```

**Functions:**
1. Collects all agent outputs
2. Assembles ReAct reasoning chain
3. Updates session memory
4. Tracks used tools
5. Returns structured response

---

## State Management

### GraphState TypedDict

```python
class GraphState(TypedDict):
    user_query: str                      # Input query
    session_memory: SessionMemory        # Conversation context
    classification: Optional[QueryClassification]  # Router output
    react_chain: List[ReActThought]     # Reasoning steps
    agent_outputs: Dict[str, Any]       # Specialist outputs
    final_answer: Optional[AgentResponse]  # Synthesizer output
    execution_log: List[str]            # Execution trace
    errors: List[str]                   # Error messages
    retry_count: int                    # Retry counter
```

### State Transitions

```
Initial State (user_query=Q)
    ↓
After Router: + classification
    ↓
After Specialist: + agent_outputs[agent_type]
    ↓
After Synthesizer: + final_answer, updated session_memory
    ↓
Final State (ready to return)
```

### SessionMemory Dataclass

```python
@dataclass
class SessionMemory:
    session_id: str                           # Unique session ID
    user_profile: Dict[str, Any]             # User info
    conversation_history: List[Dict]         # Chat history
    previous_questions: List[str]            # Past queries
    learned_topics: List[str]                # Topics covered
```

---

## Execution Flow

### Complete Execution Trace for Query "Explain ReAct"

```
[1] USER INPUT
    └─ Query: "Explain the ReAct pattern..."

[2] ROUTER NODE
    └─ Action: Classify query
    └─ Output: QueryClassification(query_type="theory", agent_path=[...])
    └─ State Update: classification = QueryClassification(...)

[3] CONDITIONAL ROUTING
    └─ Evaluate: route_to_agents(state)
    └─ Result: "theory_explainer"

[4] THEORY EXPLAINER NODE
    └─ Check: query_type == "theory" ✓
    └─ Action: Generate explanation
    └─ Output: TheoryExplanation(topic="ReAct", ...)
    └─ State Update: agent_outputs["theory"] = TheoryExplanation(...)

[5] SYNTHESIZER NODE
    └─ Input: All agent outputs
    └─ Action 1: Collect ReAct thoughts from all nodes
    └─ Action 2: Update session memory with conversation
    └─ Action 3: Create AgentResponse
    └─ State Update: final_answer = AgentResponse(...),
                    session_memory = updated(...)

[6] GRAPH END
    └─ Return: final_state with all outputs
```

---

## Tool Calling & Integration

### Tool Types

#### 1. Knowledge Base Tool
**Purpose:** Retrieve relevant information
**Simulated:** Yes (returns mock data)
**Real Implementation:** Vector DB (Chroma/Pinecone)
```python
knowledge_base_tool(query: str) -> List[str]
  # Returns: List of relevant documents/concepts
```

#### 2. Python Executor Tool
**Purpose:** Execute and validate Python code
**Simulated:** Yes (returns mock results)
**Real Implementation:** Sandboxed Python executor
```python
python_executor_tool(code: str) -> Dict
  # Returns: {"output": "...", "error": None}
```

#### 3. Save Note Tool
**Purpose:** Persist information (notes, plans)
**Simulated:** Yes (returns success)
**Real Implementation:** File storage or database
```python
save_note_tool(title: str, content: str) -> bool
  # Returns: True if saved successfully
```

### Tool Invocation Points

```
Router Agent
  ✗ No tools

Theory Explainer
  ✓ knowledge_base_tool (query: topic)

Design Advisor
  ✗ No tools

Code Helper
  ✓ python_executor_tool (code: solution)

Planner Agent
  ✓ save_note_tool (title: goal, content: plan)

Synthesizer
  ✗ No tools
```

---

## Memory Management

### Session Memory Lifecycle

```
[SESSION START]
    └─ session_id = "lab2_session_1"
    └─ conversation_history = []
    └─ previous_questions = []
    └─ learned_topics = []

[QUERY 1: "Explain ReAct"]
    └─ Router processes
    └─ Theory agent processes
    └─ Synthesizer updates:
       - conversation_history.append(q1)
       - previous_questions.append(q1)
       - learned_topics.extend([ReAct, Thought, Action])

[QUERY 2: "Compare ReAct vs standard"]
    └─ Router reads memory:
       - Knows about previous ReAct question
       - Can provide context
    └─ Theory agent processes with context
    └─ Synthesizer updates memory again

[SESSION END]
    └─ Save to JSON: memory.to_json()
    └─ Load on new session: SessionMemory.from_json()
```

### Memory Usage in Agents

#### Router Node - Memory Reading
```python
# Uses previous_questions to understand user pattern
if state.session_memory.previous_questions:
    context = "Previously asked about: " + str(previous_questions[-3:])
    # Could influence classification accuracy
```

#### Theory Explainer - Memory Enhancement
```python
# Can avoid re-explaining known topics
if query_topic in session_memory.learned_topics:
    # Could provide more advanced explanation
```

#### Synthesizer - Memory Writing
```python
# Always updates conversation history
memory.conversation_history.append({
    "query": state.user_query,
    "response": final_answer,
    "agents_used": list(agent_outputs.keys())
})
memory.previous_questions.append(state.user_query)
```

---

## ReAct Pattern Implementation

### ReActThought Data Model

```python
@dataclass
class ReActThought:
    thought: str              # Internal reasoning
    action: str              # What the agent did
    observation: str         # Result of action
```

### Example: Complete ReAct Chain for "Explain ReAct"

```
Step 1 - Router:
  Thought:    "This is asking for a definition"
  Action:     "Classify as theory query"
  Observation: "Type=theory, Complexity=medium"

Step 2 - Theory Explainer:
  Thought:    "Need to explain ReAct pattern with concepts"
  Action:     "Generate comprehensive explanation"
  Observation: "Generated 5 key concepts, confidence=0.92"

Step 3 - Synthesizer:
  Thought:    "Combine all outputs into final answer"
  Action:     "Assemble ReAct chain and update memory"
  Observation: "Processed by 3 agents, topics added to memory"
```

### Transparency Benefits

✅ **Debugging:** Can see where agent made decisions
✅ **Validation:** Can verify reasoning is logical
✅ **Explanability:** Can show user how answer was derived
✅ **Improvement:** Can identify points to optimize

---

## Error Handling

### Retry Logic (PydanticParserWithRetry)

```
[1] First LLM Call
    └─ Parse output as JSON
    └─ Validate against Pydantic model
    └─ Success? ✓ Return
    └─ Failure? Continue...

[2] Retry 1: Ask LLM to fix
    └─ Send correction prompt with schema
    └─ LLM corrects JSON
    └─ Try parsing again
    └─ Success? ✓ Return
    └─ Failure? Continue...

[3] Retry 2: Stricter correction
    └─ More detailed error message
    └─ Simpler schema
    └─ Try parsing again
    └─ Success? ✓ Return
    └─ Failure? Continue...

[4] Final Attempt
    └─ If all fail: Raise ValueError
    └─ Return fallback response
```

### Error Recovery Points

```
Router Node Fails
  └─ Return default classification (error logged)

Specialist Node Fails
  └─ Still proceed to Synthesizer
  └─ Note in final_answer that agent failed
  └─ Return partial answer

Synthesizer Fails
  └─ Return unmodified state
  └─ User sees execution log of what went wrong
```

---

## Data Flow Diagrams

### Diagram 1: Information Flow

```
User Input (Query)
    ↓
[ROUTER] Classification
    ├─ Query Type
    ├─ Complexity
    └─ Agent Path
    ↓
[CONDITIONAL SPLIT]
    ├─ theory_explainer
    ├─ design_advisor
    ├─ code_helper
    └─ planner
    ↓
[SPECIALIST PROCESSING]
    └─ Generate structured output
    └─ Create ReAct thoughts
    └─ Note tool calls
    ↓
[SYNTHESIZER]
    ├─ Collect all outputs
    ├─ Assemble ReAct chain
    ├─ Update memory
    └─ Package final answer
    ↓
Final Output (with reasoning chain)
```

### Diagram 2: State Mutations

```
Initial:
  user_query = "Explain ReAct"
  classification = None
  agent_outputs = {}
  react_chain = []
  final_answer = None

After Router:
  classification = QueryClassification(type="theory", ...)
  react_chain = [ReActThought(...)]

After Specialist:
  agent_outputs = {"theory": TheoryExplanation(...)}
  react_chain = [ReActThought(...), ReActThought(...)]

After Synthesizer:
  final_answer = AgentResponse(...)
  session_memory = updated(...)
  react_chain = [3 thoughts total]

Final State:
  All fields populated, ready to return
```

---

## Conditional Routing Rules

```
query_type    → Next Node
─────────────────────────────────
"theory"      → theory_explainer
"design"      → design_advisor
"code"        → code_helper
"planning"    → planner
None/Unknown  → synthesizer (fallback)
```

---

## Scalability Notes

### Horizontal Scaling
- **Add more agents:** 
  1. Create new agent node
  2. Create output Pydantic model
  3. Add to conditional routing
  4. Update synthesizer

- **Parallel execution:**
  - Use asyncio for independent agents
  - Combine with asyncio.gather()

### Optimization Opportunities
1. **Caching:** Cache frequent queries
2. **Batching:** Process multiple queries simultaneously
3. **Streaming:** Stream responses token-by-token
4. **Embedding:** Use vector DB for memory retrieval

---

## Conclusion

This architecture provides:

✅ **Modularity:** 6 independent agents
✅ **Transparency:** ReAct reasoning chain
✅ **Robustness:** Error handling & retries
✅ **Extensibility:** Easy to add new agents
✅ **Context-Aware:** Session memory across queries
✅ **Type-Safe:** Pydantic models ensure valid outputs

The system is production-ready for Lab 2 submission and serves as a solid foundation for more advanced multi-agent systems.

---

*Document Version: 1.0*
*Last Updated: December 2024*
