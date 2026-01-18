# Task 4 – Reflection

## What Worked Well
- **Modularity**: Multi-agent design with specialists allowed for very focused prompts.
- **Memory Retriever Agent**: Implementing a dedicated node for context retrieval (RAG-style) allowed specialists to remain lean while still having access to all historical data. This worked exceptionally well for complex productivity tasks.
- **LangGraph Orchestration**: The state-based approach provided a clear flow.
- **Real Tool Execution**: Moving from simulated to real Python execution added significant value, making the assistant "useful" rather than just "conversational."

## Unexpected Behavior / Failures
- **Dependency Issues**: Local environment setup (missing Rust for some packages) was a hurdle. This highlights the importance of standardized environments (e.g., Docker) for MAS deployment.
- **Parsing Complexity**: Structured Pydantic outputs occasionally failed on complex responses, requiring nested retry logic which added latency.

## Future Extensions
If given more time, I would:
1. **Implement a Reviewer Agent**: Add a node that critiques the specialist's output before synthesis to improve quality further.
2. **Vector DB for Memory**: Instead of a flat `notes.txt`, use a small vector store to allow RAG-style semantic search over all previous sessions and study materials.
3. **Parallel Execution**: Allow the Router to trigger multiple specialists simultaneously when a query crosses domains (e.g., a "Code + Design" question).
