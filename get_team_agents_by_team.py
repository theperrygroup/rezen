#!/usr/bin/env python3
"""
Script to get all agents on your team by first finding your team ID.
"""

import json
import os
from typing import Any, Dict, List

from rezen.agents import AgentsClient
from rezen.exceptions import RezenError
from rezen.teams import TeamsClient


def get_user_teams_and_agents(api_key: str) -> List[Dict[str, Any]]:
    """
    Get user's teams and then get all agents for those teams.

    Args:
        api_key: ReZEN API key for authentication

    Returns:
        List of all agents on the user's teams
    """
    agents_client = AgentsClient(api_key=api_key)
    teams_client = TeamsClient(api_key=api_key)

    all_team_agents = []

    try:
        # First, get the current user's information
        print("Getting your agent information...")
        me = agents_client.get_me()
        print(
            f"Authenticated as: {me.get('firstName', '')} {me.get('lastName', '')} ({me.get('email', '')})"
        )
        print(f"Agent ID: {me.get('id', '')}")
        print("-" * 50)

        # Check if the user has team information in their profile
        user_team_id = None
        if "teamId" in me:
            user_team_id = me["teamId"]
            print(f"Found team ID in profile: {user_team_id}")
        elif "team" in me and isinstance(me["team"], dict) and "id" in me["team"]:
            user_team_id = me["team"]["id"]
            print(f"Found team ID in team object: {user_team_id}")

        # If we found a team ID directly, use that
        if user_team_id:
            print(f"Getting team members for team: {user_team_id}")
            try:
                team_members = teams_client.get_team_members(user_team_id)
                print(f"Team members response type: {type(team_members)}")
                if isinstance(team_members, dict):
                    print(f"Team members response keys: {list(team_members.keys())}")

                # Extract agents from team members response
                if "members" in team_members:
                    all_team_agents.extend(team_members["members"])
                elif "agents" in team_members:
                    all_team_agents.extend(team_members["agents"])
                elif "content" in team_members:
                    all_team_agents.extend(team_members["content"])
                else:
                    all_team_agents.append(team_members)

            except Exception as team_error:
                print(f"Error getting team members: {str(team_error)}")
                # Try getting full team info instead
                try:
                    team_info = teams_client.get_team(user_team_id)
                    print(f"Team info response type: {type(team_info)}")
                    if isinstance(team_info, dict):
                        print(f"Team info response keys: {list(team_info.keys())}")

                    if "agents" in team_info:
                        all_team_agents.extend(team_info["agents"])
                    elif "members" in team_info:
                        all_team_agents.extend(team_info["members"])

                except Exception as team_info_error:
                    print(f"Error getting team info: {str(team_info_error)}")
        else:
            # Search for teams the user might be associated with
            print("No direct team ID found. Searching for teams...")
            try:
                # Search for teams with various criteria
                team_search = teams_client.search_teams(page_size=100)
                print(f"Team search response type: {type(team_search)}")
                if isinstance(team_search, dict):
                    print(f"Team search response keys: {list(team_search.keys())}")

                teams = []
                if "content" in team_search:
                    teams = team_search["content"]
                elif "teams" in team_search:
                    teams = team_search["teams"]
                elif "data" in team_search:
                    teams = team_search["data"]
                elif isinstance(team_search, list):
                    teams = team_search

                print(f"Found {len(teams)} teams in search")

                # Try to get members for each team (this might fail if not authorized)
                for team in teams[
                    :5
                ]:  # Limit to first 5 teams to avoid too many API calls
                    team_id = team.get("id")
                    team_name = team.get("name", "Unknown")
                    print(f"Checking team: {team_name} ({team_id})")

                    try:
                        members = teams_client.get_team_members(team_id)
                        if "members" in members:
                            all_team_agents.extend(members["members"])
                        elif "agents" in members:
                            all_team_agents.extend(members["agents"])
                    except Exception as member_error:
                        print(f"Cannot access team {team_name}: {str(member_error)}")
                        continue

            except Exception as search_error:
                print(f"Error searching teams: {str(search_error)}")

        return all_team_agents

    except Exception as e:
        print(f"Error in main process: {str(e)}")
        print(f"Error type: {type(e)}")
        if hasattr(e, "status_code"):
            print(f"Status code: {e.status_code}")
        if hasattr(e, "response_data"):
            print(f"Response data: {e.response_data}")
        return []


def format_agent_info(agent: Dict[str, Any]) -> str:
    """
    Format agent information for display.

    Args:
        agent: Agent data dictionary

    Returns:
        Formatted string representation of agent info
    """
    # Handle different possible field names
    first_name = agent.get("firstName", agent.get("first_name", ""))
    last_name = agent.get("lastName", agent.get("last_name", ""))
    name = f"{first_name} {last_name}".strip()

    email = agent.get("email", agent.get("emailAddress", "N/A"))
    agent_id = agent.get("id", agent.get("agentId", "N/A"))
    phone = agent.get("phone", agent.get("phoneNumber", "N/A"))
    status = agent.get("status", "N/A")
    role = agent.get("role", agent.get("teamRole", "N/A"))

    return f"• {name} | Email: {email} | Phone: {phone} | Status: {status} | Role: {role} | ID: {agent_id}"


def main() -> None:
    """Main function to execute the script."""
    # Get API key from environment or use the provided one
    api_key = os.getenv("REZEN_API_KEY", "real_Qp1vOeBFiVevF3XV0APgznZ2frPp8fSlaqq7")

    print("ReZEN Team Agents Retrieval (by Team ID)")
    print("=" * 50)

    agents = get_user_teams_and_agents(api_key)

    if agents:
        print(f"\nFound {len(agents)} agents on your team(s):")
        print("=" * 50)

        for i, agent in enumerate(agents, 1):
            print(f"{i:3d}. {format_agent_info(agent)}")

        print("\n" + "=" * 50)
        print(f"Total agents: {len(agents)}")

        # Save to JSON file for reference
        with open("team_agents_by_team.json", "w") as f:
            json.dump(agents, f, indent=2, default=str)
        print("Agent data saved to 'team_agents_by_team.json'")

    else:
        print("No team agents found or unable to retrieve team agent data.")


if __name__ == "__main__":
    main()
