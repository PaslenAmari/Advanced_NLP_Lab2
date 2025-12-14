# config.py
"""
Configuration: LLM client setup and Pydantic parser with retry logic.
"""

import os
import json
import time
from typing import Any, Dict
from pydantic import ValidationError, BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.messages import HumanMessage


# ============================================================================
# LLM Client Setup
# ============================================================================

def get_llm_client():
    """
    Initialize ChatOpenAI client connected to vLLM server.
    Uses environment variables:
    - LITELLM_BASE_URL (or hardcoded default)
    - OPENAI_API_KEY
    - MODEL_NAME
    """
    base_url = os.getenv("LITELLM_BASE_URL", "http://a6k2.dgx:34000/v1")
    api_key = os.getenv("OPENAI_API_KEY", "sk-pyB6Xy4h3c428_a3Jyktcg")
    model = os.getenv("MODEL_NAME", "qwen3-30b-vl")
    
    print("[LLM] Connecting to {} with model {}".format(base_url, model))
    
    return ChatOpenAI(
        base_url=base_url,
        api_key=api_key,
        model=model,
        temperature=0.7,
        max_retries=2
    )


# ============================================================================
# Pydantic Parser with Retry Logic
# ============================================================================

class PydanticParserWithRetry:
    """
    Wrapper around PydanticOutputParser that handles JSON extraction
    and parsing errors with retry logic.
    
    Features:
    - Extracts JSON from LLM output even if surrounded by text
    - Retries with correction prompts if parsing fails
    - Graceful degradation on max retries
    """
    
    def __init__(self, pydantic_model, llm_client, max_retries: int = 3):
        self.model = pydantic_model
        self.llm = llm_client
        self.max_retries = max_retries
        self.base_parser = PydanticOutputParser(pydantic_object=pydantic_model)
    
    def parse_with_retry(self, llm_output: str) -> Any:
        """
        Attempt to parse LLM output with retries.
        
        Strategy:
        1. Extract JSON from output
        2. Parse JSON into Pydantic model
        3. On failure: ask LLM to fix and retry
        
        Args:
            llm_output: Raw string from LLM
            
        Returns:
            Parsed Pydantic model instance
            
        Raises:
            ValueError: After max_retries attempts fail
        """
        for attempt in range(self.max_retries):
            try:
                # Extract JSON from output
                if isinstance(llm_output, str):
                    if "{" in llm_output and "}" in llm_output:
                        start = llm_output.find("{")
                        end = llm_output.rfind("}") + 1
                        json_str = llm_output[start:end]
                    else:
                        json_str = llm_output
                else:
                    json_str = str(llm_output)
                
                # Parse JSON
                data = json.loads(json_str)
                result = self.model(**data)
                print("OK: Parsed {} successfully".format(self.model.__name__))
                return result
            
            except (ValidationError, json.JSONDecodeError) as e:
                if attempt == self.max_retries - 1:
                    print("FAILED: After {} attempts".format(self.max_retries))
                    raise ValueError("Parser failed: {}".format(str(e)))
                
                print("[RETRY {}] {}".format(attempt + 1, type(e).__name__))
                
                # Ask LLM to fix the JSON
                format_instructions = self.base_parser.get_format_instructions()
                correction_prompt = (
                    "Fix JSON error. Schema: {}. Original: {}. "
                    "Return ONLY valid JSON.".format(
                        format_instructions, llm_output[:300]
                    )
                )
                
                try:
                    corrected = self.llm.invoke([HumanMessage(content=correction_prompt)])
                    llm_output = corrected.content
                except Exception as retry_error:
                    print("Retry failed: {}".format(retry_error))
                    continue
        
        return None
    
    def invoke_with_retry(self, prompt: PromptTemplate, input_dict: Dict) -> Any:
        """
        Build and invoke LLM chain with retry logic.
        
        Args:
            prompt: LangChain PromptTemplate
            input_dict: Input variables for prompt
            
        Returns:
            Parsed Pydantic model instance
        """
        for attempt in range(self.max_retries):
            try:
                chain = prompt | self.llm
                output = chain.invoke(input_dict)
                
                if hasattr(output, 'content'):
                    return self.parse_with_retry(output.content)
                else:
                    return self.parse_with_retry(str(output))
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                print("[CHAIN RETRY {}] {}".format(attempt + 1, str(e)[:80]))
                time.sleep(0.5 * (attempt + 1))