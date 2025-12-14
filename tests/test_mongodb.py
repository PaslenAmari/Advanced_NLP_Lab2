"""
test MongoDB persistence with caching and monitoring
demonstrates:
- storing queries and responses in MongoDB
- tracking execution metrics
- exporting session data
"""

import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src import build_graph, SessionMemory
from src.cache import get_cache, get_deduplicator
from mongodb_storage import get_adapter, close_adapter


def test_with_mongodb_persistence():
    """run test with MongoDB persistence"""
    
    print("\n" + "="*80)
    print("  ADVANCED NLP LAB 2 - MONGODB PERSISTENCE TEST".center(80))
    print("="*80 + "\n")
    
    # Initialize components
    db = get_adapter()
    cache = get_cache()
    dedup = get_deduplicator()
    graph = build_graph()
    session = SessionMemory(session_id="mongodb_test")
    
    print(f" Session ID: {session.session_id}\n")
    
    # Test queries
    test_queries = [
        "what is machine learning?",
        "explain machine learning",
        "what is machine learning?",
        "how to build neural networks",
        "how to build neural networks?",
    ]
    
    query_count = 0
    response_count = 0
    
    print("Executing queries with MongoDB persistence...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f">>> Query {i}: '{query}'")
        
        # Check cache first
        cached = cache.get(query)
        if cached:
            print("    Retrieved from cache")
            # Store in DB that this was cached
            query_id = db.store_query(
                session_id=session.session_id,
                query=query,
                query_type=cached.get("routing", "unknown"),
                query_hash=cache.get_hash(query)
            )
            if query_id:
                db.db.queries.update_one(
                    {"_id": __import__('bson').ObjectId(query_id)},
                    {"$set": {"cached": True}}
                )
            continue
        
        # Check deduplication
        dup = dedup.find_duplicate(query)
        if dup:
            print("    Found similar query")
            query_id = db.store_query(
                session_id=session.session_id,
                query=query,
                query_type=dup.get("routing", "unknown"),
                query_hash=cache.get_hash(query)
            )
            if query_id:
                db.db.queries.update_one(
                    {"_id": __import__('bson').ObjectId(query_id)},
                    {"$set": {"deduped": True}}
                )
            cache.put(query, dup, execution_time=0.001)
            continue
        
        # Execute new query
        print("     Executing...")
        start = time.time()
        query_count += 1
        
        # Store query in DB
        query_id = db.store_query(
            session_id=session.session_id,
            query=query,
            query_type="unknown",  # Will update after classification
            query_hash=cache.get_hash(query)
        )
        
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
            exec_time = time.time() - start
            response_count += 1
            
            routing = result.get('classification').query_type if result.get('classification') else 'unknown'
            agents = list(result.get('agent_outputs', {}).keys())
            react_chain = result.get('react_chain', [])
            logs = result.get('execution_log', [])
            errors = result.get('errors', [])
            
            cache_entry = {
                "routing": routing,
                "agents": agents,
                "errors": len(errors),
            }
            
            # Store response in DB
            if query_id:
                response_id = db.store_response(
                    query_id=query_id,
                    session_id=session.session_id,
                    routing=routing,
                    agents_used=agents,
                    final_answer=result.get('final_answer', ''),
                    execution_time=exec_time,
                    react_chain=react_chain
                )
                
                # Store execution log
                db.store_execution_log(
                    session_id=session.session_id,
                    log_entries=logs,
                    agents=agents,
                    errors=errors
                )
            
            # Store cache stats
            cache.put(query, cache_entry, execution_time=exec_time)
            dedup.register(query, cache_entry)
            
            cache_stats = cache.get_stats()
            db.store_cache_stats(
                hits=cache_stats['hits'],
                misses=cache_stats['misses'],
                cache_size=cache_stats['cache_size'],
                time_saved=cache_stats['total_saved_time_seconds'],
                hit_rate=cache_stats['hit_rate_percent']
            )
            
            print(f"    Done in {exec_time:.2f}s (routing: {routing})")
            
            session = result['session_memory']
            
        except Exception as e:
            print(f"    Error: {str(e)[:60]}")
    
    # Print statistics
    print("\n" + "="*80)
    print(" STATISTICS".center(80))
    print("="*80 + "\n")
    
    print(" Query Execution:")
    print(f"  Total Queries: {len(test_queries)}")
    print(f"  New Queries Executed: {query_count}")
    print(f"  Responses Generated: {response_count}")
    print(f"  Cache Hits: {cache.get_stats()['hits']}")
    print(f"  Hit Rate: {cache.get_stats()['hit_rate_percent']:.1f}%")
    
    print("\n MongoDB Storage:")
    db_stats = db.get_statistics()
    if "error" not in db_stats:
        print(f"  Total Queries Stored: {db_stats['total_queries']}")
        print(f"  Total Responses Stored: {db_stats['total_responses']}")
        print(f"  Total Sessions: {db_stats['total_sessions']}")
        print(f"  Total Errors: {db_stats['total_errors']}")
        
        if db_stats.get('latest_cache_stats'):
            latest = db_stats['latest_cache_stats']
            print(f"  Latest Cache Hit Rate: {latest.get('hit_rate', 0):.1f}%")
            print(f"  Time Saved (Latest): {latest.get('time_saved', 0):.2f}s")
    else:
        print(f"  {db_stats['error']}")
    
    # Export session data
    print("\n Session Export:")
    export_file = f"session_{session.session_id}.json"
    if db.export_session_to_json(session.session_id, export_file):
        print(f" Session exported to {export_file}")
    
    # Print sample session data
    session_history = db.get_session_history(session.session_id)
    print(f"\n Session History Summary:")
    print(f"  Session ID: {session_history['session_id']}")
    print(f"  Total Queries: {session_history['query_count']}")
    print(f"  Responses: {len(session_history['responses'])}")
    print(f"  Execution Logs: {len(session_history['execution_logs'])}")
    
    # Close connection
    close_adapter()
    
    print("\n" + "="*80)
    print(" Test complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_with_mongodb_persistence()