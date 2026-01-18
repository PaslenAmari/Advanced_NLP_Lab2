# tools.py
"""
Actual tool implementations for the Multi-Agent System.
"""

import os
import json
import subprocess
import tempfile
from typing import Dict, List, Any

def execute_python(code: str) -> str:
    """
    Executes Python code and returns the output.
    Uses a temporary file for safety.
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        
        result = subprocess.run(
            ["python3", tmp_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        os.unlink(tmp_path)
        
        if result.returncode == 0:
            return result.stdout if result.stdout else "Success (no output)"
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Execution failed: {str(e)}"

def save_to_notes(content: str, filename: str = "notes.txt") -> str:
    """
    Saves or appends content to a local notes file.
    """
    try:
        # Get the project root directory
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(root_dir, filename)
        
        with open(file_path, "a") as f:
            f.write("\n" + "="*40 + "\n")
            f.write(content)
            f.write("\n" + "="*40 + "\n")
        
        return f"Successfully saved to {filename}"
    except Exception as e:
        return f"Failed to save note: {str(e)}"

def read_notes(filename: str = "notes.txt") -> str:
    """
    Reads all saved notes from the persistent notes file.
    Acts as a simple 'retrieval' mechanism for memory.
    """
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(root_dir, filename)
        
        if not os.path.exists(file_path):
            return "No notes found yet."
            
        with open(file_path, "r") as f:
            content = f.read()
            
        return content if content else "Notes file is empty."
    except Exception as e:
        return f"Failed to read notes: {str(e)}"

def query_knowledge_base(topic: str) -> str:
    """
    Simulates a knowledge base query by looking into a local JSON file.
    If no file exists, it returns a default explanation.
    """
    kb_data = {
        "react": "The ReAct pattern combines reasoning and acting. The agent generates a thought, performs an action, and then observes the result.",
        "langgraph": "LangGraph is a library for building stateful, multi-actor applications with LLMs, built on top of LangChain.",
        "multi-agent system": "A multi-agent system (MAS) is a computerized system composed of multiple interacting intelligent agents."
    }
    
    # Try to find a match (case-insensitive)
    topic_lower = topic.lower()
    for key, value in kb_data.items():
        if key in topic_lower:
            return value
            
    return f"No specific information found for '{topic}' in the local knowledge base."

def get_available_tools() -> Dict[str, Any]:
    """Returns metadata for available tools."""
    return {
        "python_executor": {
            "func": execute_python,
            "description": "Executes Python code and returns output. Use for calculations or logic verification."
        },
        "note_taker": {
            "func": save_to_notes,
            "description": "Saves information to a persistent notes file. Use for long-term memory."
        },
        "note_reader": {
            "func": read_notes,
            "description": "Reads all previously saved notes. Use to retrieve context from earlier sessions."
        },
        "knowledge_base": {
            "func": query_knowledge_base,
            "description": "Retrieves information about specific study topics (ReAct, LangGraph, etc.)."
        }
    }
