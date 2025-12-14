print("=" * 60)
print("testing imports...")
print("=" * 60)

# test 1: models
try:
    from src.models import GraphState, SessionMemory, QueryClassification
    print(" test 1: models imported successfully")
except Exception as e:
    print(f" test 1 failed: {e}")
    exit(1)

# test 2: config
try:
    from src.config import get_llm_client, PydanticParserWithRetry
    print(" test 2: config imported successfully")
except Exception as e:
    print(f" test 2 failed: {e}")
    exit(1)

# test 3: agents
try:
    from src.agents import router_node, theory_explainer_node
    print(" test 3: agents imported successfully")
except Exception as e:
    print(f" test 3 failed: {e}")
    exit(1)

# test 4: graph
try:
    from src.graph import build_graph
    print(" test 4: graph imported successfully")
except Exception as e:
    print(f" test 4 failed: {e}")
    exit(1)

# test 5: full package
try:
    from src import GraphState, build_graph
    print(" test 5: full package imported successfully")
except Exception as e:
    print(f" test 5 failed: {e}")
    exit(1)

print("=" * 60)
print(" all imports successful! ready to run main.py")
print("=" * 60)
