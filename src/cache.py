"""
query caching and optimization for multi-agent system
"""

import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class QueryCache:
    """
    cache for query results to avoid recomputation
    features:
    - hash-based query matching
    - ttl (time to live) expiration
    - memory efficiency
    - cache statistics
    """
    
    def __init__(self, max_size: int = 100, ttl_minutes: int = 60):
        """
        initialize cache
        
        args:
            max_size: maximum number of cached queries
            ttl_minutes: time to live in minutes
        """
        self.cache = {}
        self.max_size = max_size
        self.ttl = timedelta(minutes=ttl_minutes)
        self.stats = {
            "hits": 0,
            "misses": 0,
            "total_saved_time": 0.0,
        }
    
    def get_hash(self, query: str) -> str:
        """
        create hash of query for fast lookup
        
        args:
            query: user query string
            
        returns:
            md5 hash of query
        """
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def get(self, query: str) -> Optional[Dict]:
        """
        retrieve cached result if available
        
        args:
            query: user query
            
        returns:
            cached result or none
        """
        query_hash = self.get_hash(query)
        
        if query_hash not in self.cache:
            self.stats["misses"] += 1
            return None
        
        entry = self.cache[query_hash]
        
        # check if expired
        if datetime.now() > entry["expires"]:
            del self.cache[query_hash]
            self.stats["misses"] += 1
            return None
        
        # cache hit!
        self.stats["hits"] += 1
        self.stats["total_saved_time"] += entry["execution_time"]
        
        print(f" cache hit! saved {entry['execution_time']:.2f}s")
        return entry["result"]
    
    def put(self, query: str, result: Dict, execution_time: float):
        """
        store query result in cache
        
        args:
            query: user query
            result: execution result
            execution_time: time taken to execute
        """
        query_hash = self.get_hash(query)
        
        # remove oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k]["timestamp"]
            )
            del self.cache[oldest_key]
        
        self.cache[query_hash] = {
            "query": query,
            "result": result,
            "execution_time": execution_time,
            "timestamp": datetime.now(),
            "expires": datetime.now() + self.ttl,
        }
        
        print(f" cached query (cache size: {len(self.cache)}/{self.max_size})")
    
    def clear(self):
        """clear all cache"""
        self.cache.clear()
    
    def get_stats(self) -> Dict:
        """
        get cache statistics
        
        returns:
            dict with cache performance metrics
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (
            (self.stats["hits"] / total_requests * 100)
            if total_requests > 0 else 0
        )
        
        return {
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "hit_rate_percent": hit_rate,
            "total_saved_time_seconds": self.stats["total_saved_time"],
            "avg_saved_per_hit": (
                self.stats["total_saved_time"] / self.stats["hits"]
                if self.stats["hits"] > 0 else 0
            ),
        }


class RequestDeduplicator:
    """
    deduplicate similar queries to avoid duplicate processing
    """
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        initialize deduplicator
        
        args:
            similarity_threshold: threshold for considering queries similar (0-1)
        """
        self.processed_queries = {}
        self.threshold = similarity_threshold
    
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """calculate edit distance between strings"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def similarity(self, q1: str, q2: str) -> float:
        """
        calculate similarity between two queries (0-1)
        """
        s1 = q1.lower().strip()
        s2 = q2.lower().strip()
        
        if s1 == s2:
            return 1.0
        
        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
        
        distance = self.levenshtein_distance(s1, s2)
        return 1.0 - (distance / max_len)
    
    def find_duplicate(self, query: str) -> Optional[Dict]:
        """
        find similar query in history
        
        args:
            query: new query
            
        returns:
            previously processed similar query or none
        """
        for prev_query, result in self.processed_queries.items():
            sim = self.similarity(query, prev_query)
            if sim >= self.threshold:
                print(
                    f"found similar query "
                    f"(similarity: {sim:.1%}): '{prev_query}'"
                )
                return result
        
        return None
    
    def register(self, query: str, result: Dict):
        """register processed query"""
        self.processed_queries[query] = result


# global cache instance
_cache = QueryCache(max_size=100, ttl_minutes=60)
_deduplicator = RequestDeduplicator(similarity_threshold=0.80)


def get_cache() -> QueryCache:
    """get global cache instance"""
    return _cache


def get_deduplicator() -> RequestDeduplicator:
    """get global deduplicator instance"""
    return _deduplicator