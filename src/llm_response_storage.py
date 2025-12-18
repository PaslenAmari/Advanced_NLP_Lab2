"""
Extended MongoDB schema for LLM responses and conversations
stores complete LLM interactions with metadata
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pymongo import MongoClient
import json


class LLMResponseStorage:
    """
    specialized storage for LLM responses and conversations
    tracks:
    - raw LLM outputs
    - prompt templates
    - model information
    - token usage
    - latency metrics
    - conversation history
    """
    
    def __init__(self, db):
        """
        initialize LLM response storage
        
        args:
        - db: MongoDB database instance
        """
        self.db = db
        self._create_llm_collections()
    
    def _create_llm_collections(self):
        """create LLM-specific collections"""
        
        # Raw LLM responses
        if "llm_responses" not in self.db.list_collection_names():
            self.db.create_collection("llm_responses")
            self.db.llm_responses.create_index("session_id")
            self.db.llm_responses.create_index("agent")
            self.db.llm_responses.create_index("model")
            self.db.llm_responses.create_index("timestamp")
        
        # Conversation history
        if "conversations" not in self.db.list_collection_names():
            self.db.create_collection("conversations")
            self.db.conversations.create_index("session_id")
            self.db.conversations.create_index("agent")
        
        # Prompts used
        if "prompts" not in self.db.list_collection_names():
            self.db.create_collection("prompts")
            self.db.prompts.create_index("agent")
            self.db.prompts.create_index("prompt_hash")
        
        # Token usage statistics
        if "token_usage" not in self.db.list_collection_names():
            self.db.create_collection("token_usage")
            self.db.token_usage.create_index("session_id")
            self.db.token_usage.create_index("agent")
        
        # Model performance metrics
        if "model_metrics" not in self.db.list_collection_names():
            self.db.create_collection("model_metrics")
            self.db.model_metrics.create_index("model")
            self.db.model_metrics.create_index("timestamp")
    
    def store_llm_response(
        self,
        session_id: str,
        agent: str,
        model: str,
        prompt: str,
        response: str,
        raw_output: Dict[str, Any],
        temperature: float,
        max_tokens: int,
        latency: float,
        tokens_used: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        store complete LLM response with all metadata
        
        args:
            session_id: session identifier
            agent: which agent called LLM (router/theory/design/etc)
            model: model name (qwen3-30b-vl/etc)
            prompt: full prompt sent to LLM
            response: parsed response from LLM
            raw_output: complete raw output from API
            temperature: temperature parameter used
            max_tokens: max tokens parameter
            latency: response time in seconds
            tokens_used: {prompt_tokens, completion_tokens, total_tokens}
            metadata: additional metadata
            
        returns:
            document ID if successful
        """
        try:
            doc = {
                "session_id": session_id,
                "agent": agent,
                "model": model,
                "timestamp": datetime.now(),
                
                # Prompt info
                "prompt": prompt,
                "prompt_length": len(prompt),
                
                # Response info
                "response": response,
                "response_length": len(response),
                
                # Raw API output
                "raw_output": raw_output,
                
                # Parameters
                "parameters": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                
                # Performance metrics
                "latency_seconds": latency,
                "tokens_used": tokens_used or {},
                
                # Additional metadata
                "metadata": metadata or {},
            }
            
            result = self.db.llm_responses.insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing LLM response: {e}")
            return None
    
    def store_conversation_turn(
        self,
        session_id: str,
        agent: str,
        turn_number: int,
        user_message: str,
        assistant_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        store single conversation turn
        
        args:
            session_id: session identifier
            agent: agent type
            turn_number: conversation turn number
            user_message: user input
            assistant_response: assistant response
            context: additional context
            
        returns:
            document ID if successful
        """
        try:
            doc = {
                "session_id": session_id,
                "agent": agent,
                "turn_number": turn_number,
                "timestamp": datetime.now(),
                
                "messages": [
                    {
                        "role": "user",
                        "content": user_message,
                        "timestamp": datetime.now(),
                    },
                    {
                        "role": "assistant",
                        "content": assistant_response,
                        "timestamp": datetime.now(),
                    }
                ],
                
                "context": context or {},
            }
            
            result = self.db.conversations.insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing conversation turn: {e}")
            return None
    
    def store_prompt_template(
        self,
        agent: str,
        prompt_template: str,
        system_message: Optional[str] = None,
        description: Optional[str] = None,
        variables: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        store prompt template for later analysis
        
        args:
        - agent: agent using this prompt
        - prompt_template: template text
        - system_message: system message (if used)
        - description: prompt description
        - variables: template variables
            
        returns:
        - document ID if successful
        """
        try:
            import hashlib
            prompt_hash = hashlib.md5(prompt_template.encode()).hexdigest()
            
            doc = {
                "agent": agent,
                "prompt_hash": prompt_hash,
                "prompt_template": prompt_template,
                "system_message": system_message,
                "description": description,
                "variables": variables or [],
                "timestamp": datetime.now(),
            }
            
            # Check if already exists
            existing = self.db.prompts.find_one({"prompt_hash": prompt_hash})
            if existing:
                return str(existing["_id"])
            
            result = self.db.prompts.insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing prompt template: {e}")
            return None
    
    def store_token_usage(
        self,
        session_id: str,
        agent: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        cost: Optional[float] = None
    ) -> Optional[str]:
        """
        store token usage statistics
        
        args:
            session_id: session identifier
            agent: agent name
            model: model name
            prompt_tokens: tokens in prompt
            completion_tokens: tokens in response
            total_tokens: total tokens
            cost: estimated cost
            
        returns:
            document ID if successful
        """
        try:
            doc = {
                "session_id": session_id,
                "agent": agent,
                "model": model,
                "timestamp": datetime.now(),
                
                "tokens": {
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                    "total": total_tokens,
                },
                
                "cost": cost,
            }
            
            result = self.db.token_usage.insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing token usage: {e}")
            return None
    
    def store_model_metrics(
        self,
        model: str,
        agent: str,
        latency: float,
        success: bool,
        error: Optional[str] = None,
        retry_count: int = 0
    ) -> Optional[str]:
        """
        store model performance metrics
        
        args:
            model: model name
            agent: agent type
            latency: response time
            success: was call successful?
            error: error message if failed
            retry_count: number of retries needed
            
        returns:
            document ID if successful
        """
        try:
            doc = {
                "model": model,
                "agent": agent,
                "timestamp": datetime.now(),
                
                "latency_seconds": latency,
                "success": success,
                "error": error,
                "retry_count": retry_count,
            }
            
            result = self.db.model_metrics.insert_one(doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing model metrics: {e}")
            return None
    
    def get_conversation_by_session(self, session_id: str) -> List[Dict]:
        """
        retrieve full conversation for session
        
        args:
            session_id: session identifier
            
        returns:
            list of conversation turns
        """
        try:
            convos = list(self.db.conversations.find(
                {"session_id": session_id}
            ).sort("turn_number", 1))
            return convos
        except Exception as e:
            print(f"Error retrieving conversations: {e}")
            return []
    
    def get_llm_responses_by_session(self, session_id: str) -> List[Dict]:
        """
        retrieve all LLM responses for session
        
        args:
            session_id: session identifier
            
        returns:
            list of LLM responses
        """
        try:
            responses = list(self.db.llm_responses.find(
                {"session_id": session_id}
            ).sort("timestamp", 1))
            return responses
        except Exception as e:
            print(f"Error retrieving LLM responses: {e}")
            return []
    
    def get_token_usage_summary(self, session_id: str) -> Dict[str, Any]:
        """
        get token usage summary for session
        
        args:
            session_id: session identifier
            
        returns:
            dict with token usage statistics
        """
        try:
            tokens = list(self.db.token_usage.find(
                {"session_id": session_id}
            ))
            
            total_prompt = sum(t["tokens"]["prompt"] for t in tokens)
            total_completion = sum(t["tokens"]["completion"] for t in tokens)
            total = sum(t["tokens"]["total"] for t in tokens)
            total_cost = sum(t.get("cost", 0) for t in tokens if t.get("cost"))
            
            return {
                "session_id": session_id,
                "tokens_prompt": total_prompt,
                "tokens_completion": total_completion,
                "tokens_total": total,
                "estimated_cost": total_cost,
                "num_calls": len(tokens),
            }
        except Exception as e:
            print(f"Error getting token usage summary: {e}")
            return {}
    
    def get_model_performance_stats(self, model: str) -> Dict[str, Any]:
        """
        get performance statistics for a model
        
        args:
        - model: model name
            
        returns:
        - dict with performance metrics
        """
        try:
            metrics = list(self.db.model_metrics.find({"model": model}))
            
            if not metrics:
                return {"error": f"No metrics found for {model}"}
            
            latencies = [m["latency_seconds"] for m in metrics]
            successes = sum(1 for m in metrics if m["success"])
            total = len(metrics)
            
            return {
                "model": model,
                "total_calls": total,
                "success_rate": (successes / total * 100) if total > 0 else 0,
                "avg_latency": sum(latencies) / len(latencies) if latencies else 0,
                "min_latency": min(latencies) if latencies else 0,
                "max_latency": max(latencies) if latencies else 0,
                "total_retries": sum(m.get("retry_count", 0) for m in metrics),
            }
        except Exception as e:
            print(f"Error getting model stats: {e}")
            return {}
    
    def export_llm_conversation(
        self,
        session_id: str,
        filename: str,
        include_raw_output: bool = False
    ) -> bool:
        """
        export LLM conversation to JSON file
        
        args:
        - session_id: session identifier
        - filename: output filename
        - include_raw_output: include raw API responses?
            
        returns:
        - True if successful
        """
        try:
            convos = self.get_conversation_by_session(session_id)
            responses = self.get_llm_responses_by_session(session_id)
            token_summary = self.get_token_usage_summary(session_id)
            
            export_data = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "conversation_turns": convos,
                "llm_responses": responses if include_raw_output else [
                    {k: v for k, v in r.items() if k != "raw_output"}
                    for r in responses
                ],
                "token_usage_summary": token_summary,
            }
            
            def convert_objectid(obj):
                if isinstance(obj, dict):
                    return {k: convert_objectid(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_objectid(item) for item in obj]
                elif hasattr(obj, '__str__') and 'ObjectId' in str(type(obj)):
                    return str(obj)
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                return obj
            
            export_data = convert_objectid(export_data)
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            print(f"Exported LLM conversation to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting conversation: {e}")
            return False