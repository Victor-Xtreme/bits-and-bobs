"""
RepoSense WatsonX Orchestrate Client
Handles all interactions with IBM WatsonX Orchestrate agents
"""

import json
import asyncio
import logging
import time
from typing import Any, Dict, Optional
import httpx

from .config import settings

logger = logging.getLogger(__name__)

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"


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
        self._iam_token: Optional[str] = None
        self._iam_token_expiry: float = 0.0

        # Agent IDs
        self.architect_agent_id = settings.orchestrate_agent_architect_id
        self.reviewer_agent_id = settings.orchestrate_agent_reviewer_id
        self.documenter_agent_id = settings.orchestrate_agent_documenter_id
        self.hardener_agent_id = settings.orchestrate_agent_hardener_id
        self.environment_id = settings.orchestrate_environment_id
        self.instance_id = settings.orchestrate_instance_id

    async def _get_iam_token(self) -> str:
        """Exchange IBM Cloud API key for an IAM Bearer token, refreshing when near expiry."""
        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "ORCHESTRATE_API_KEY is missing or empty. Open RepoSense setup and save your Orchestrate API key."
            )
        if self._iam_token and time.time() < self._iam_token_expiry - 60:
            return self._iam_token
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                IAM_TOKEN_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": self.api_key,
                }
            )
            if response.status_code != 200:
                raise ValueError(f"IAM token exchange failed ({response.status_code}): {response.text[:300]}")
            token_data = response.json()
            self._iam_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self._iam_token_expiry = time.time() + expires_in
            return self._iam_token

    def _auth_headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
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
        url = f"{self.base_url}/instances/{self.instance_id}/v1/orchestrate/{agent_id}/chat/completions"
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }

        logger.info(f"Calling {agent_name} agent (ID: {agent_id})")

        try:
            token = await self._get_iam_token()
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    headers=self._auth_headers(token),
                    json=payload
                )

                if response.status_code == 401:
                    self._iam_token = None
                    raise ValueError(f"Authentication failed (401). URL: {url} | {response.text[:300]}")
                elif response.status_code == 404:
                    raise ValueError(f"Agent endpoint not found (404). URL: {url} | {response.text[:300]}")
                elif response.status_code >= 500:
                    raise ConnectionError(f"Server error {response.status_code}. URL: {url} | {response.text[:300]}")
                elif response.status_code != 200:
                    raise ValueError(f"API error {response.status_code}. URL: {url} | {response.text[:300]}")

                logger.info(f"{agent_name} raw response ({response.status_code}): {response.text[:500]}")
                result = response.json()
                logger.info(f"{agent_name} response keys: {list(result.keys())}")

                if "choices" in result:
                    return result["choices"][0]["message"]["content"]
                elif "output" in result:
                    out = result["output"]
                    return out if isinstance(out, str) else json.dumps(out)
                elif "content" in result:
                    content = result["content"]
                    if isinstance(content, list):
                        texts = [c.get("text", "") for c in content if isinstance(c, dict)]
                        return " ".join(texts)
                    return content if isinstance(content, str) else json.dumps(content)
                elif "message" in result:
                    m = result["message"]
                    if isinstance(m, dict):
                        return m.get("content", json.dumps(m))
                    return m if isinstance(m, str) else json.dumps(m)
                elif "text" in result:
                    return result["text"]
                else:
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