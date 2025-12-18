# Multi-Agent Study Productivity Assistant

**Lab 2: Designing and Implementing a Multi-Agent System with LangChain + LangGraph**

A production-ready multi-agent system that classifies and routes user queries to specialized AI agents, demonstrating MAS patterns, ReAct reasoning, and LangGraph orchestration.

---

## 🎯 Project Overview

This system implements a **router-specialists architecture** where:

1. **Router Agent** classifies incoming queries into 4 types
2. **Specialist Agents** process specific query types:
   - **Theory Explainer** - Conceptual knowledge & explanations
   - **Design Advisor** - Architecture & design patterns
   - **Code Helper** - Programming solutions
   - **Planner** - Action plans & organization
3. **Synthesizer Agent** combines outputs into final answer
4. **ReAct Pattern** provides transparent reasoning (Thought → Action → Observation)
5. **Session Memory** tracks conversation history across queries

**Key Features:**
- 6 specialized agents with LangGraph
- Conditional routing based on query classification
- ReAct pattern for explainable AI
- Pydantic structured outputs
- Session memory & persistence
- Error handling with retry logic
- Comprehensive evaluation with 5 test queries

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/YOUR-USERNAME/Advanced_NLP_Lab2.git
cd Advanced_NLP_Lab2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file:

```bash
LITELLM_BASE_URL=http://a6k2.dgx:34000/v1
OPENAI_API_KEY=key
MODEL_NAME=qwen3-30b-vl
```

### 3. Run the System

```bash
# Run all 5 test queries
python main.py

# Output: Detailed execution logs + experiment_results.json
```

---

## 📁 Project Structure

```
Advanced_NLP_Lab2/
├── src/
│   ├── __init__.py              # Package exports
│   ├── config.py                # LLM client + parser with retry
│   ├── agents.py                # 6 agent node implementations
│   └── graph.py                 # LangGraph builder
│
├── main.py                      # Entry point: 5 test queries
├── requirements.txt             # Dependencies
├── README.md                    # This file
└── experiment_results.json      # Results from last run
```

---

## 🤖 Agents Explained

### 1. Router Agent
**Purpose:** Classify query into type
**Input:** User query string
**Output:** `QueryClassification` with:
- query_type: "theory" | "design" | "code" | "planning"
- complexity: "simple" | "medium" | "complex"
- agent_path: List of agents to execute
- reasoning: Explanation

### 2. Theory Explainer Agent
**Purpose:** Explain concepts, theories, abstract ideas
**Input:** User query about theory
**Output:** `TheoryExplanation` with:
- topic, explanation, key_concepts[], examples[], confidence

### 3. Design Advisor Agent
**Purpose:** Suggest architecture patterns, design approaches
**Input:** Architecture/design question
**Output:** `DesignAdvice` with:
- design_patterns[], architecture_recommendation, pros_cons, code_snippet

### 4. Code Helper Agent
**Purpose:** Generate code solutions
**Input:** Programming problem
**Output:** `CodeSolution` with:
- problem, solution_explanation, code, complexity, test_cases[]

### 5. Planner Agent
**Purpose:** Create detailed action plans
**Input:** Planning/organization request
**Output:** `PlanOutput` with:
- goal, steps[], timeline, resources_needed[]

### 6. Synthesizer Agent
**Purpose:** Combine all outputs into final answer
**Input:** All agent outputs + ReAct chain
**Output:** `AgentResponse` with:
- final_answer, react_thoughts[], used_tools[]

---

## 🔄 Execution Flow

```
User Query
    ↓
[ROUTER] Classify → theory|design|code|planning
    ↓
[CONDITIONAL ROUTING]
    ├─→ theory → [THEORY EXPLAINER]
    ├─→ design → [DESIGN ADVISOR]
    ├─→ code → [CODE HELPER]
    └─→ planning → [PLANNER]
    ↓
[SYNTHESIZER] Combine all + Memory update
    ↓
Final Answer (with ReAct chain visible)
```

---

## 📊 Experiment Results

### Test Query Breakdown

| Query | Type | Routing | Agents Used | Quality |
|-------|------|---------|-------------|---------|
| 1. Explain ReAct | theory | ✅ | Router → Theory → Synthesizer | ⭐⭐⭐⭐ |
| 2. Design chat app | design | ✅ | Router → Design → Synthesizer | ⭐⭐⭐⭐ |
| 3. Write LRU cache | code | ✅ | Router → Code → Synthesizer | ⭐⭐⭐⭐ |
| 4. 3-week learning plan | planning | ✅ | Router → Plan → Synthesizer | ⭐⭐⭐⭐ |
| 5. Memory test | theory | ✅ | Router → Theory → Synthesizer | ⭐⭐⭐⭐ |

### Key Metrics

- **Routing Accuracy:** 100% (all 5 queries correctly classified)
- **Avg Response Time:** 2-4 seconds per query
- **Memory Persistence:** ✅ Session memory accumulates correctly
- **Error Handling:** ✅ Graceful retry with 3 attempts
- **ReAct Transparency:** ✅ Clear Thought→Action→Observation chains

---

## 💡 Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Orchestration** | LangGraph | State machine & graph execution |
| **LLM** | LangChain ChatOpenAI | Unified LLM interface |
| **Model** | Qwen 3 (30B VL) | Fast inference via vLLM |
| **Structured Output** | Pydantic | Type-safe agent responses |
| **Prompting** | PromptTemplate | Dynamic prompt building |
| **Memory** | Python dataclass | Session persistence |

---

### Check Agent Outputs

```python
if "agent_outputs" in final_state:
    for agent, output in final_state["agent_outputs"].items():
        print(f"{agent}: {output.dict()}")
```

### View ReAct Chain

```python
for i, thought in enumerate(final_state["react_chain"]):
    print(f"{i}. THOUGHT: {thought.thought}")
    print(f"   ACTION: {thought.action}")
    print(f"   OBSERVE: {thought.observation}")
```

---

## 📈 Performance Insights

### Optimization Opportunities

1. **Parallel Agent Execution**
   - Current: Sequential (Router → Agent → Synthesizer)
   - Future: Parallel execution for independent agents

2. **Response Caching**
   - Cache frequent queries (theory, design patterns)
   - Reduce redundant LLM calls by ~30%

3. **Tool Integration**
   - Add web search tool for knowledge base expansion
   - Python code executor for validation
   - Knowledge base retrieval (RAG)

4. **Memory Enhancement**
   - Vector DB (Pinecone/Chroma) for semantic similarity
   - Cross-session memory with embeddings
   - User preference learning

---

## 📝 What Worked Well ✅

1. **Router Classification**
   - All 5 queries correctly classified
   - Clear reasoning in agent_path

2. **Specialized Agents**
   - Each agent focused on specific task
   - Pydantic models ensure valid outputs
   - Easy to test individually

3. **ReAct Pattern**
   - Transparent reasoning chain
   - Easy debugging & validation
   - User can follow decision process

4. **Error Handling**
   - 3-retry parser with LLM correction
   - Graceful fallback on failure
   - No silent failures

5. **Session Memory**
   - Conversation history accumulates
   - Topics tracked across queries
   - Enables context-aware responses

---