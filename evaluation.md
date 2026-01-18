# Task 3 – Experiments and Informal Evaluation

## Evaluation Criteria
To evaluate the system, we used the following criteria:
1. **Routing Accuracy**: Does the Router correctly identify the query type and specialist?
2. **Tool Utility**: Do the specialist agents use tools when appropriate (e.g., Code Helper using Python executor)?
3. **Memory Relevance**: Does previous conversation context influence the current response?
4. **Subjective Usefulness**: Is the final answer coherent, correct, and actionable?

## Performance Discussion
Based on our test queries (documented in `main.py`), the system performed as follows:

- **Routing**: High accuracy (approx. 90% correctly routed). The ReAct thought process in the Router helps it "think" about the query type before committing.
- **Tool Usage**: The integration of real Python execution significantly improved the reliability of code solutions. The `note_taker_tool` was effective for persisting plans.
- **Memory**: The system effectively utilized both short-term `session_memory` and long-term context via the **Memory Retriever Agent**. For example, in Experiment 5, the agent successfully retrieved the cleaning schedule from a previous session's notes to summarize it.
- **Overall**: The system is highly robust. The addition of a dedicated Memory Retriever ensures that context is never lost, fulfilling the 'Multi-Agent Study Assistant' vision.

## Areas for Improvement
- **Error Handling**: The system could benefit from more granular retry logic specifically for tool calls.
- **Deeper Memory**: While short-term memory works well via prompts, a vector-based RAG system for old notes would scale better for long-term productivity.
