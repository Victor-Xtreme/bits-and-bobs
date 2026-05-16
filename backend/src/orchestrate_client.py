"""
RepoSense WatsonX Orchestrate Client
Handles all interactions with IBM WatsonX Orchestrate agents
"""

import json
import asyncio
import logging
from typing import Any, Dict, Optional
import httpx

from .config import settings

logger = logging.getLogger(__name__)


class OrchestrateClient:
    """
    Client for interacting with WatsonX Orchestrate agents.
    Handles API calls, error handling, and response parsing.
    """
    
    def __init__(self):
        """Initialize the Orchestrate client with configuration from settings."""
        self.api_key = settings.orchestrate_api_key
        self.base_url = settings.orchestrate_url.rstrip('/')
        self.timeout = settings.orchestrate_timeout
        
        # Agent IDs
        self.architect_agent_id = settings.orchestrate_agent_architect_id
        self.reviewer_agent_id = settings.orchestrate_agent_reviewer_id
        self.documenter_agent_id = settings.orchestrate_agent_documenter_id
        self.hardener_agent_id = settings.orchestrate_agent_hardener_id
        
        # HTTP client configuration
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def _call_agent(
        self,
        agent_id: str,
        agent_name: str,
        prompt: str
    ) -> str:
        """
        Call a WatsonX Orchestrate agent with a prompt.
        
        Args:
            agent_id: The agent's unique identifier
            agent_name: Human-readable agent name for logging
            prompt: The prompt to send to the agent
            
        Returns:
            The agent's response as a string
            
        Raises:
            TimeoutError: If the request times out
            ValueError: For authentication or API errors
            ConnectionError: For network connectivity issues
        """
        url = f"{self.base_url}/agents/{agent_id}/invoke"
        
        payload = {
            "input": prompt,
            "parameters": {
                "model_id": settings.orchestrate_model_id,
                "max_tokens": 4000,
                "temperature": 0.1,
                "top_p": 1.0
            }
        }
        
        logger.info(f"Calling {agent_name} agent (ID: {agent_id})")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                
                # Check for HTTP errors
                if response.status_code == 401:
                    raise ValueError("Orchestrate authentication failed - check API key")
                elif response.status_code == 404:
                    raise ValueError(f"Agent {agent_id} not found - check agent ID")
                elif response.status_code >= 500:
                    raise ConnectionError(f"Orchestrate server error: {response.status_code}")
                elif response.status_code != 200:
                    raise ValueError(f"Orchestrate API error: {response.status_code} - {response.text}")
                
                # Parse response
                result = response.json()
                
                # Extract the generated text from the response
                # The exact structure may vary based on Orchestrate's API
                if "output" in result:
                    return result["output"]
                elif "text" in result:
                    return result["text"]
                elif "response" in result:
                    return result["response"]
                else:
                    # Fallback: return the entire result as JSON string
                    logger.warning(f"Unexpected response structure from {agent_name}: {result}")
                    return json.dumps(result)
                
        except httpx.TimeoutException:
            logger.error(f"{agent_name} agent request timed out")
            raise TimeoutError(f"{agent_name} agent request timed out after {self.timeout}s")
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to Orchestrate: {str(e)}")
            raise ConnectionError(f"Failed to connect to Orchestrate: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse {agent_name} response as JSON: {str(e)}")
            raise ValueError(f"Invalid JSON response from {agent_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error calling {agent_name}: {str(e)}", exc_info=True)
            raise
    
    def _parse_json_response(self, response: str, agent_name: str) -> Dict[str, Any]:
        """
        Parse JSON from agent response, handling markdown code blocks.
        
        Args:
            response: Raw response from agent
            agent_name: Name of the agent for error messages
            
        Returns:
            Parsed JSON as dictionary
            
        Raises:
            ValueError: If JSON parsing fails
        """
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse {agent_name} JSON response: {response[:200]}")
            raise ValueError(f"Failed to parse {agent_name} JSON response: {str(e)}")
    
    async def call_architect_agent(self, prompt: str) -> Dict[str, Any]:
        """
        Call the ARCHITECT agent to generate architecture graph.
        
        Args:
            prompt: The analysis prompt with codebase information
            
        Returns:
            Parsed JSON response with nodes and edges
        """
        response = await self._call_agent(
            self.architect_agent_id,
            "ARCHITECT",
            prompt
        )
        return self._parse_json_response(response, "ARCHITECT")
    
    async def call_reviewer_agent(self, prompt: str) -> Dict[str, Any]:
        """
        Call the REVIEWER agent to generate code review findings.
        
        Args:
            prompt: The analysis prompt with code samples
            
        Returns:
            Parsed JSON response with findings
        """
        response = await self._call_agent(
            self.reviewer_agent_id,
            "REVIEWER",
            prompt
        )
        return self._parse_json_response(response, "REVIEWER")
    
    async def call_documenter_agent(self, prompt: str) -> Dict[str, Any]:
        """
        Call the DOCUMENTER agent to generate documentation.
        
        Args:
            prompt: The analysis prompt with function information
            
        Returns:
            Parsed JSON response with docs and tests
        """
        response = await self._call_agent(
            self.documenter_agent_id,
            "DOCUMENTER",
            prompt
        )
        return self._parse_json_response(response, "DOCUMENTER")
    
    async def call_hardener_agent(self, prompt: str) -> Dict[str, Any]:
        """
        Call the HARDENER agent to find security issues and modernization opportunities.
        
        Args:
            prompt: The analysis prompt with codebase summary
            
        Returns:
            Parsed JSON response with security issues and modernization items
        """
        response = await self._call_agent(
            self.hardener_agent_id,
            "HARDENER",
            prompt
        )
        return self._parse_json_response(response, "HARDENER")


# Global client instance
_orchestrate_client: Optional[OrchestrateClient] = None


def get_orchestrate_client() -> OrchestrateClient:
    """
    Get or create the global Orchestrate client instance.
    
    Returns:
        OrchestrateClient instance
    """
    global _orchestrate_client
    if _orchestrate_client is None:
        _orchestrate_client = OrchestrateClient()
    return _orchestrate_client


# Made with Bob