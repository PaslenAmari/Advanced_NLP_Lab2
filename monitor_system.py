#!/usr/bin/env python
"""
live system monitoring dashboard for logs, cache, memory in real-time regime
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src import build_graph, SessionMemory
from src.cache import get_cache, get_deduplicator


class SystemMonitor:
    """monitor system state during execution"""
    
    def __init__(self):
        self.cache = get_cache()
        self.dedup = get_deduplicator()
        self.queries_executed = 0
        self.start_time = time.time()
    
    def print_header(self):
        """print dashboard header"""
        print("\n" + "="*80)
        print("  LIVE SYSTEM MONITORING DASHBOARD".center(80))
        print("="*80 + "\n")
    
    def print_cache_status(self):
        """print cache status"""
        stats = self.cache.get_stats()
        print(" CACHE STATUS:")
        print(f"  Size: {stats['cache_size']}/{stats['max_size']} entries")
        print(f"  Hits: {stats['hits']} | Misses: {stats['misses']}")
        print(f"  Hit Rate: {stats['hit_rate_percent']:.1f}%")
        print(f"  Time Saved: {stats['total_saved_time_seconds']:.2f}s")
        if stats['hits'] > 0:
            print(f"  Avg Time/Hit: {stats['avg_saved_per_hit']:.2f}s")
    
    def print_dedup_status(self):
        """print deduplication status"""
        print("\n DEDUPLICATION STATUS:")
        print(f"  Processed Queries: {len(self.dedup.processed_queries)}")
        print(f"  Similarity Threshold: {self.dedup.threshold:.0%}")
        print(f"  Queries in History: {len(self.dedup.processed_queries)}")
    
    def print_execution_stats(self):
        """print execution statistics"""
        elapsed = time.time() - self.start_time
        print("\n⏱  EXECUTION STATISTICS:")
        print(f"  Queries Executed: {self.queries_executed}")
        print(f"  Elapsed Time: {elapsed:.2f}s")
        if self.queries_executed > 0:
            avg_time = elapsed / self.queries_executed
            print(f"  Avg Time/Query: {avg_time:.2f}s")
    
    def print_memory_info(self):
        """print memory information"""
        print("\n MEMORY INFORMATION:")
        print(f"  Cache Entries: {len(self.cache.cache)}")
        print(f"  Dedup Entries: {len(self.dedup.processed_queries)}")
        print(f"  Total Memory Objects: {len(self.cache.cache) + len(self.dedup.processed_queries)}")
    
    def print_dashboard(self):
        """print full dashboard"""
        self.print_header()
        self.print_cache_status()
        self.print_dedup_status()
        self.print_execution_stats()
        self.print_memory_info()
        print("\n" + "="*80 + "\n")
    
    def update_query_count(self):
        """increment query counter"""
        self.queries_executed += 1


def run_monitored_test():
    """run test with live monitoring"""
    
    monitor = SystemMonitor()
    graph = build_graph()
    session = SessionMemory(session_id="monitored_test")
    
    test_queries = [
        "what is machine learning?",
        "explain machine learning",
        "what is machine learning?",
        "how to build neural networks",
    ]
    
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  MONITORING SYSTEM EXECUTION".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80 + "\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f">>> Running Query {i}: '{query}'")
        
        # Check cache
        cached = monitor.cache.get(query)
        if cached:
            print("     Retrieved from cache")
            monitor.update_query_count()
            continue
        
        # Check dedup
        dup = monitor.dedup.find_duplicate(query)
        if dup:
            print("     Found similar query, reusing")
            monitor.cache.put(query, dup, 0.001)
            monitor.update_query_count()
            continue
        
        # Execute
        print("      Executing new query...")
        start = time.time()
        
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
            
            routing = result.get('classification').query_type if result.get('classification') else 'unknown'
            agents = ', '.join(result.get('agent_outputs', {}).keys())
            
            cache_entry = {
                "routing": routing,
                "agents": agents,
                "errors": len(result.get('errors', [])),
            }
            
            monitor.cache.put(query, cache_entry, execution_time=exec_time)
            monitor.dedup.register(query, cache_entry)
            monitor.update_query_count()
            
            print(f"     Completed in {exec_time:.2f}s (routing: {routing})")
            
            session = result['session_memory']
            
        except Exception as e:
            print(f"     Error: {str(e)[:50]}")
    
    # Final dashboard
    monitor.print_dashboard()
    
    print(" Monitoring complete!\n")


if __name__ == "__main__":
    run_monitored_test()