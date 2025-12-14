#!/usr/bin/env python
"""
test caching and optimization
demonstrates:
- query result caching to avoid recomputation
- deduplication of similar queries
- performance metrics
"""

import time
import sys
from pathlib import Path

# add parent directory to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import build_graph, SessionMemory
from src.cache import get_cache, get_deduplicator


def test_caching():
    """test caching functionality"""
    
    print("=" * 80)
    print("caching and optimization test")
    print("=" * 80)
    
    # initialize
    cache = get_cache()
    dedup = get_deduplicator()
    graph = build_graph()
    session = SessionMemory(session_id="cache_test")
    
    # test queries - with duplicates and similar queries
    test_queries = [
        "what is machine learning?",
        "explain machine learning",  # similar to query 1
        "what is machine learning?",  # exact duplicate of query 1
        "how to build a neural network",
        "how to build a neural network?",  # exact duplicate
        "design a real-time chat system",
        "design a real-time chat application",  # similar to query 6
    ]
    
    print(f"\nrunning {len(test_queries)} queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n>>> query {i}: '{query}'")
        
        # check cache first
        cached_result = cache.get(query)
        if cached_result:
            print("result from cache (not recomputed)")
            print(f"  routing: {cached_result.get('routing')}")
            print(f"  agents: {cached_result.get('agents')}")
            continue
        
        # check for duplicate
        dup_result = dedup.find_duplicate(query)
        if dup_result:
            print("reusing result from similar query")
            cache.put(query, dup_result, execution_time=0.001)
            continue
        
        # execute new query
        print("executing new query...")
        start_time = time.time()
        
        state = {
            "user_query": query,
            "session_memory": session,
            "classification": None,
            "react_chain": [],
            "agent_outputs": {},
            "final_answer": None,
            "execution_log": [],
            "errors": [],
            "retry_count": 0,
        }
        
        try:
            result = graph.invoke(state)
            exec_time = time.time() - start_time
            
            # extract routing info
            routing = (
                result.get('classification').query_type 
                if result.get('classification') else 'unknown'
            )
            agents = ', '.join(result.get('agent_outputs', {}).keys())
            
            # store in cache
            cache_entry = {
                "routing": routing,
                "agents": agents,
                "errors": len(result.get('errors', [])),
            }
            cache.put(query, cache_entry, execution_time=exec_time)
            
            print(f"  routing: {routing}")
            print(f"  agents: {agents}")
            print(f"  time: {exec_time:.2f}s")
            
            # register for deduplication
            dedup.register(query, cache_entry)
            
            # update session
            session = result['session_memory']
            
        except Exception as e:
            print(f"  error: {str(e)[:80]}")
    
    # print statistics
    print("\n" + "=" * 80)
    print("caching statistics")
    print("=" * 80)
    
    stats = cache.get_stats()
    print(f"\ncache size: {stats['cache_size']}/{stats['max_size']}")
    print(f"cache hits: {stats['hits']}")
    print(f"cache misses: {stats['misses']}")
    print(f"hit rate: {stats['hit_rate_percent']:.1f}%")
    print(f"total time saved: {stats['total_saved_time_seconds']:.2f}s")
    if stats['total_saved_time_seconds'] > 0:
        print(f"avg time per cache hit: {stats['avg_saved_per_hit']:.2f}s")
    
    print(f"\ndeduplication:")
    print(f"  processed queries: {len(dedup.processed_queries)}")
    print(f"  dedup threshold: {dedup.threshold:.0%}")
    
    print("\n" + "=" * 80)
    print("test complete!")
    print("=" * 80)


if __name__ == "__main__":
    test_caching()