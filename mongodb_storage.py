"""
MongoDB adapter for persistent storage of:
- query logs
- responses
- execution traces
- cache statistics
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import json


class MongoDBAdapter:
    """
    adapter for MongoDB persistent storage
    handles all database operations for the system
    """
    
    def __init__(
        self,
        uri: str = "mongodb://localhost:27018",
        db_name: str = "anlp_lab2",
        timeout: int = 5000
    ):
        """
        initialize MongoDB connection
        
        args:
            uri: MongoDB connection string
            db_name: database name
            timeout: connection timeout in ms
        """
        self.uri = uri
        self.db_name = db_name
        self.timeout = timeout
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """establish MongoDB connection"""
        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=self.timeout,
                connectTimeoutMS=self.timeout
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self._create_collections()
            print(f" MongoDB connected: {self.uri}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f" MongoDB connection failed: {e}")
            print("  Using in-memory storage (not persistent)")
            self.client = None
            self.db = None
    
    def _create_collections(self):
        """create necessary collections if they don't exist"""
        if not self.db:
            return
        
        # Create collections with indexes
        if "queries" not in self.db.list_collection_names():
            self.db.create_collection("queries")
            self.db.queries.create_index("session_id")
            self.db.queries.create_index("timestamp")
            self.db.queries.create_index("query_hash")
        
        if "responses" not in self.db.list_collection_names():
            self.db.create_collection("responses")
            self.db.responses.create_index("query_id")
            self.db.responses.create_index("session_id")
        
        if "execution_logs" not in self.db.list_collection_names():
            self.db.create_collection("execution_logs")
            self.db.execution_logs.create_index("session_id")
            self.db.execution_logs.create_index("timestamp")
        
        if "cache_stats" not in self.db.list_collection_names():
            self.db.create_collection("cache_stats")
            self.db.cache_stats.create_index("timestamp")
    
    def store_query(
        self,
        session_id: str,
        query: str,
        query_type: str,
        query_hash: str
    ) -> Optional[str]:
        """
        store query in database
        
        args:
            session_id: session identifier
            query: query text
            query_type: classification (theory/design/code/planning)
            query_hash: MD5 hash of query
            
        returns:
            document ID if successful, None otherwise
        """
        if not self.db:
            return None
        
        try:
            doc = {
                "session_id": session_id,
                "query": query,
                "query_type": query_type,
                "query_hash": query_hash,
                "timestamp": datetime.now(),
                "cached": False,
                "deduped": False,
            }
            result = self.db.queries.insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing query: {e}")
            return None
    
    def store_response(
        self,
        query_id: str,
        session_id: str,
        routing: str,
        agents_used: List[str],
        final_answer: str,
        execution_time: float,
        react_chain: List[Dict]
    ) -> Optional[str]:
        """
        store response in database
        
        args:
            query_id: ID of corresponding query
            session_id: session identifier
            routing: routing decision
            agents_used: list of agents that executed
            final_answer: final synthesized answer
            execution_time: time taken (seconds)
            react_chain: list of reasoning steps
            
        returns:
            document ID if successful, None otherwise
        """
        if not self.db:
            return None
        
        try:
            doc = {
                "query_id": query_id,
                "session_id": session_id,
                "routing": routing,
                "agents_used": agents_used,
                "final_answer": final_answer,
                "execution_time": execution_time,
                "react_chain": react_chain,
                "timestamp": datetime.now(),
            }
            result = self.db.responses.insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing response: {e}")
            return None
    
    def store_execution_log(
        self,
        session_id: str,
        log_entries: List[str],
        agents: List[str],
        errors: List[str]
    ) -> Optional[str]:
        """
        store execution log in database
        
        args:
            session_id: session identifier
            log_entries: list of log messages
            agents: agents that executed
            errors: any errors encountered
            
        returns:
            document ID if successful, None otherwise
        """
        if not self.db:
            return None
        
        try:
            doc = {
                "session_id": session_id,
                "log_entries": log_entries,
                "agents": agents,
                "errors": errors,
                "timestamp": datetime.now(),
                "error_count": len(errors),
            }
            result = self.db.execution_logs.insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing execution log: {e}")
            return None
    
    def store_cache_stats(
        self,
        hits: int,
        misses: int,
        cache_size: int,
        time_saved: float,
        hit_rate: float
    ) -> Optional[str]:
        """
        store cache statistics
        
        args:
            hits: number of cache hits
            misses: number of cache misses
            cache_size: current cache size
            time_saved: total time saved
            hit_rate: hit rate percentage
            
        returns:
            document ID if successful, None otherwise
        """
        if not self.db:
            return None
        
        try:
            doc = {
                "hits": hits,
                "misses": misses,
                "cache_size": cache_size,
                "time_saved": time_saved,
                "hit_rate": hit_rate,
                "timestamp": datetime.now(),
            }
            result = self.db.cache_stats.insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing cache stats: {e}")
            return None
    
    def get_session_history(self, session_id: str) -> Dict[str, Any]:
        """
        retrieve full session history
        
        args:
            session_id: session identifier
            
        returns:
            dict with queries, responses, logs
        """
        if not self.db:
            return {"error": "Database not connected"}
        
        try:
            queries = list(self.db.queries.find(
                {"session_id": session_id},
                {"_id": 1, "query": 1, "query_type": 1, "timestamp": 1}
            ))
            
            responses = list(self.db.responses.find(
                {"session_id": session_id},
                {"_id": 1, "routing": 1, "agents_used": 1, "execution_time": 1}
            ))
            
            logs = list(self.db.execution_logs.find(
                {"session_id": session_id},
                {"_id": 1, "log_entries": 1, "error_count": 1}
            ))
            
            return {
                "session_id": session_id,
                "query_count": len(queries),
                "queries": queries,
                "responses": responses,
                "execution_logs": logs,
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        get overall system statistics from database
        
        returns:
            dict with statistics
        """
        if not self.db:
            return {"error": "Database not connected"}
        
        try:
            total_queries = self.db.queries.count_documents({})
            total_responses = self.db.responses.count_documents({})
            total_sessions = len(
                self.db.queries.distinct("session_id")
            )
            
            # Get latest cache stats
            latest_cache = self.db.cache_stats.find_one(
                sort=[("timestamp", -1)]
            )
            
            # Get error count
            error_logs = self.db.execution_logs.find(
                {"error_count": {"$gt": 0}}
            )
            total_errors = sum(log["error_count"] for log in error_logs)
            
            return {
                "total_queries": total_queries,
                "total_responses": total_responses,
                "total_sessions": total_sessions,
                "total_errors": total_errors,
                "latest_cache_stats": latest_cache,
            }
        except Exception as e:
            return {"error": str(e)}
    
    def export_session_to_json(
        self,
        session_id: str,
        filename: str
    ) -> bool:
        """
        export session data to JSON file
        
        args:
            session_id: session identifier
            filename: output filename
            
        returns:
            True if successful, False otherwise
        """
        try:
            history = self.get_session_history(session_id)
            
            # Convert ObjectIds to strings
            def convert_objectid(obj):
                if isinstance(obj, dict):
                    return {k: convert_objectid(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_objectid(item) for item in obj]
                elif hasattr(obj, '__str__') and 'ObjectId' in str(type(obj)):
                    return str(obj)
                return obj
            
            history = convert_objectid(history)
            
            with open(filename, 'w') as f:
                json.dump(history, f, indent=2, default=str)
            
            print(f" Exported to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def close(self):
        """close MongoDB connection"""
        if self.client:
            self.client.close()
            print(" MongoDB connection closed")


# Global adapter instance
_adapter = None


def get_adapter(
    uri: str = "mongodb://localhost:27018",
    db_name: str = "anlp_lab2"
) -> MongoDBAdapter:
    """
    get or create MongoDB adapter instance
    
    args:
        uri: MongoDB connection string
        db_name: database name
        
    returns:
        MongoDBAdapter instance
    """
    global _adapter
    if _adapter is None:
        _adapter = MongoDBAdapter(uri=uri, db_name=db_name)
    return _adapter


def close_adapter():
    """close global adapter"""
    global _adapter
    if _adapter:
        _adapter.close()
        _adapter = None