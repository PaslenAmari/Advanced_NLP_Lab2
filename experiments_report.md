# Task 3: Experiment Recording & Evaluation (Sample Report)

This report details the results of running the five required test queries through the Multi-Agent System.

---

### Experiment 1: [THEORY]
- **Description**: Conceptual/theoretical question about MAS/LLM agents
- **Query**: `Explain the difference between ReAct and Plan-and-Solve patterns in Multi-Agent Systems. Use your knowledge base tool.`
- **Node Execution Order**: START → router → memory_retriever → theory_explainer → synthesizer → END
- **Tools Invoked**: `note_reader`, `knowledge_base_tool`
- **Memory Usage**: 
    - Read: Retrieved empty long-term context from notes.
    - Write: Updated conversation history with ReAct theory.
- **Usefulness**: Yes. The agent provided a clear distinction and used the KB tool to verify definitions.
- **Improvements**: Could include a diagram of each pattern.

---

### Experiment 2: [DESIGN]
- **Description**: Design/architecture question
- **Query**: `Design a scalable microservices architecture for a real-time analytics dashboard. Suggest patterns.`
- **Node Execution Order**: START → router → memory_retriever → design_advisor → synthesizer → END
- **Tools Invoked**: `note_reader`
- **Memory Usage**: 
    - Read: Retrieved previous ReAct theory (irrelevant for design but loaded).
    - Write: Updated history with microservices recommendations (Pub-Sub, Event Sourcing).
- **Usefulness**: Yes. The advice was structurally sound and followed industry standards.
- **Improvements**: Suggest specific database choices (e.g., ClickHouse).

---

### Experiment 3: [CODE]
- **Description**: Implementation/coding question
- **Query**: `Write a Python function to calculate the Fibonacci sequence up to N. Use the python executor to verify.`
- **Node Execution Order**: START → router → memory_retriever → code_helper → synthesizer → END
- **Tools Invoked**: `note_reader`, `python_executor_tool`
- **Memory Usage**: 
    - Read: Previous turns in session history.
    - Write: Updated history with verified code.
- **Usefulness**: Yes. The code was executed and verified to be correct before being returned to the user.
- **Improvements**: Add time complexity analysis in the final output.

---

### Experiment 4: [PRODUCTIVITY]
- **Description**: Everyday tasks / productivity
- **Query**: `Create a cleaning schedule for a 2-bedroom apartment for the next month. Save it to my notes.`
- **Node Execution Order**: START → router → memory_retriever → planner → synthesizer → END
- **Tools Invoked**: `note_reader`, `note_taker_tool`
- **Memory Usage**: 
    - Read: General session context.
    - Write: **Saved plan to notes.txt** for long-term persistence.
- **Usefulness**: Yes. Created a structured weekly schedule.
- **Improvements**: Allow exporting to .csv format.

---

### Experiment 5: [PRODUCTIVITY + MEMORY TEST]
- **Description**: Everyday tasks / productivity + Memory test
- **Query**: `What was the cleaning schedule we just created? Summarize it.`
- **Node Execution Order**: START → router → memory_retriever → planner → synthesizer → END
- **Tools Invoked**: `note_reader` (RAG-style retrieval)
- **Memory Usage**: 
    - Read: **Successfully retrieved the schedule from notes.txt** (Long-term memory).
    - Write: Updated history with summary.
- **Usefulness**: Yes. The agent "remembered" the schedule despite it potentially being from a previous turn or session.
- **Improvements**: Suggest starting the first task today.

---
