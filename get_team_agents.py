#!/usr/bin/env python3
"""
Script to get all agents on your team using the ReZEN API.
"""

import json
import os
from typing import Any, Dict, List

from rezen.agents import AgentsClient
from rezen.exceptions import RezenError


def get_all_team_agents(api_key: str) -> List[Dict[str, Any]]:
    """
    Get all agents on the team using the ReZEN API.

    Args:
        api_key: ReZEN API key for authentication

    Returns:
        List of all active agents on the team
    """
    client = AgentsClient(api_key=api_key)

    all_agents: List[Dict[str, Any]] = []
    page_number = 0
    page_size = 20  # Default page size

    try:
        # First, let's get the current user's information
        print("Getting your agent information...")
        me = client.get_me()
        print(
            f"Authenticated as: {me.get('firstName', '')} {me.get('lastName', '')} ({me.get('email', '')})"
        )
        print(f"Agent ID: {me.get('id', '')}")
        print("-" * 50)

        # Get all active agents with pagination
        print("Fetching all active agents...")
        while True:
            try:
                response = client.get_active_agents(
                    page_number=page_number, page_size=page_size
                )
                print(f"Response for page {page_number}: {type(response)}")
                if isinstance(response, dict):
                    print(f"Response keys: {list(response.keys())}")

                # Handle different response formats
                agents_data: List[Dict[str, Any]] = []
                if isinstance(response, dict):
                    if "content" in response and isinstance(response["content"], list):
                        agents_data = response["content"]
                    elif "data" in response and isinstance(response["data"], list):
                        agents_data = response["data"]
                    elif "agents" in response and isinstance(response["agents"], list):
                        agents_data = response["agents"]
                    else:
                        # Response might be a single agent
                        agents_data = [response]
                elif isinstance(response, list):
                    agents_data = response

                print(f"Found {len(agents_data)} agents on page {page_number}")

                if not agents_data:
                    break

                all_agents.extend(agents_data)

                # Check if there are more pages
                if len(agents_data) < page_size:
                    break

                page_number += 1

            except Exception as page_error:
                print(f"Error on page {page_number}: {str(page_error)}")
                print(f"Error type: {type(page_error)}")
                if hasattr(page_error, "status_code"):
                    print(f"Status code: {page_error.status_code}")
                if hasattr(page_error, "response_data"):
                    print(f"Response data: {page_error.response_data}")
                break

        return all_agents

    except Exception as e:
        print(f"Error fetching agents: {str(e)}")
        print(f"Error type: {type(e)}")
        if hasattr(e, "status_code"):
            print(f"Status code: {e.status_code}")
        if hasattr(e, "response_data"):
            print(f"Response data: {e.response_data}")

        # Let's also try the search method as a fallback
        try:
            print("Trying alternative search method...")
            response = client.search_active_agents(page_size=100)
            print(f"Search response type: {type(response)}")
            if isinstance(response, dict):
                print(f"Search response keys: {list(response.keys())}")
                if "content" in response:
                    content = response["content"]
                    if isinstance(content, list):
                        return content
                    else:
                        return []
            elif isinstance(response, list):
                return response
            else:
                return []
        except Exception as e2:
            print(f"Error with search method: {str(e2)}")
            print(f"Search error type: {type(e2)}")
            if hasattr(e2, "status_code"):
                print(f"Search status code: {e2.status_code}")
            if hasattr(e2, "response_data"):
                print(f"Search response data: {e2.response_data}")
            return []


def format_agent_info(agent: Dict[str, Any]) -> str:
    """
    Format agent information for display.

    Args:
        agent: Agent data dictionary

    Returns:
        Formatted string representation of agent info
    """
    name = f"{agent.get('firstName', '')} {agent.get('lastName', '')}".strip()
    email = agent.get("email", "N/A")
    agent_id = agent.get("id", "N/A")
    phone = agent.get("phone", "N/A")
    status = agent.get("status", "N/A")

    return f"• {name} | Email: {email} | Phone: {phone} | Status: {status} | ID: {agent_id}"


def main() -> None:
    """Main function to execute the script."""
    # Get API key from environment or use the provided one
    api_key = os.getenv("REZEN_API_KEY", "real_Qp1vOeBFiVevF3XV0APgznZ2frPp8fSlaqq7")

    print("ReZEN Team Agents Retrieval")
    print("=" * 50)

    agents = get_all_team_agents(api_key)

    if agents:
        print(f"\nFound {len(agents)} active agents on your team:")
        print("=" * 50)

        for i, agent in enumerate(agents, 1):
            print(f"{i:3d}. {format_agent_info(agent)}")

        print("\n" + "=" * 50)
        print(f"Total agents: {len(agents)}")

        # Save to JSON file for reference
        with open("team_agents.json", "w") as f:
            json.dump(agents, f, indent=2, default=str)
        print("Agent data saved to 'team_agents.json'")

    else:
        print("No agents found or unable to retrieve agent data.")


if __name__ == "__main__":
    main()
