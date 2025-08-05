#!/usr/bin/env python3
"""
Script to get all agents on your specific teams using the team IDs from your profile.
"""

import json
import os
from typing import Any, Dict, List

from rezen.agents import AgentsClient
from rezen.teams import TeamsClient


def get_my_team_agents(api_key: str) -> List[Dict[str, Any]]:
    """
    Get all agents from the user's teams.

    Args:
        api_key: ReZEN API key for authentication

    Returns:
        List of all agents from the user's teams
    """
    agents_client = AgentsClient(api_key=api_key)
    teams_client = TeamsClient(api_key=api_key)

    try:
        # Get current user info to extract team IDs
        me = agents_client.get_me()
        print(
            f"Getting teams for agent: {me.get('firstName', '')} {me.get('lastName', '')}"
        )

        all_agents = []
        user_teams = me.get("teams", [])

        if not user_teams:
            print("No teams found in user profile!")
            return []

        print(f"\nFound {len(user_teams)} team(s) in your profile:")
        print("=" * 60)

        for team_info in user_teams:
            team_id = team_info.get("teamId")
            team_name = team_info.get("teamName", "Unknown Team")
            team_type = team_info.get("teamType", "Unknown")
            roles = team_info.get("teamRoles", [])
            is_leader = team_info.get("isLeader", False)
            is_admin = team_info.get("isAdmin", False)

            print(f"\nTeam: {team_name} ({team_type})")
            print(f"ID: {team_id}")
            print(f"Your roles: {', '.join(roles)}")
            print(f"Leader: {is_leader}, Admin: {is_admin}")
            print("-" * 60)

            if not team_id:
                print("  No team ID found, skipping...")
                continue

            # Try to get team members
            try:
                print(f"  Getting members for {team_name}...")
                team_members = teams_client.get_team_members(team_id)

                if isinstance(team_members, dict):
                    print(f"  Team members response keys: {list(team_members.keys())}")

                    # Extract agents from response
                    agents_found = 0
                    if "members" in team_members:
                        members = team_members["members"]
                        agents_found = len(members)
                        for member in members:
                            member["source_team_id"] = team_id
                            member["source_team_name"] = team_name
                            member["source_team_type"] = team_type
                            all_agents.append(member)
                    elif "agents" in team_members:
                        agents = team_members["agents"]
                        agents_found = len(agents)
                        for agent in agents:
                            agent["source_team_id"] = team_id
                            agent["source_team_name"] = team_name
                            agent["source_team_type"] = team_type
                            all_agents.append(agent)
                    elif "content" in team_members:
                        content = team_members["content"]
                        agents_found = len(content)
                        for agent in content:
                            agent["source_team_id"] = team_id
                            agent["source_team_name"] = team_name
                            agent["source_team_type"] = team_type
                            all_agents.append(agent)
                    else:
                        print(f"  Unexpected response structure for {team_name}")
                        print(
                            f"  Response: {json.dumps(team_members, indent=2, default=str)[:500]}..."
                        )

                    print(f"  Found {agents_found} agent(s) in {team_name}")

            except Exception as team_error:
                print(f"  Error getting members for {team_name}: {str(team_error)}")

                # Try getting full team info as fallback
                try:
                    print(f"  Trying get_team for {team_name}...")
                    full_team = teams_client.get_team(team_id)

                    if isinstance(full_team, dict) and "agents" in full_team:
                        agents = full_team["agents"]
                        for agent in agents:
                            agent["source_team_id"] = team_id
                            agent["source_team_name"] = team_name
                            agent["source_team_type"] = team_type
                            all_agents.append(agent)
                        print(f"  Found {len(agents)} agent(s) via get_team")
                    else:
                        print(f"  No agents found in full team response")

                except Exception as full_team_error:
                    print(f"  Error with get_team: {str(full_team_error)}")

        return all_agents

    except Exception as e:
        print(f"Error getting team agents: {str(e)}")
        return []


def format_agent_info(agent: Dict[str, Any]) -> str:
    """
    Format agent information for display.

    Args:
        agent: Agent data dictionary

    Returns:
        Formatted string representation of agent info
    """
    # Handle different possible structures
    if "agent" in agent:
        agent_data = agent["agent"]
        first_name = agent_data.get("firstName", "")
        last_name = agent_data.get("lastName", "")
        email = agent_data.get("emailAddress", "N/A")
        phone = agent_data.get("phoneNumber", "N/A")
        status = agent_data.get("agentStatus", "N/A")
        roles = ", ".join(agent.get("roles", []))
    else:
        first_name = agent.get("firstName", "")
        last_name = agent.get("lastName", "")
        email = agent.get("emailAddress", agent.get("email", "N/A"))
        phone = agent.get("phoneNumber", agent.get("phone", "N/A"))
        status = agent.get("agentStatus", agent.get("status", "N/A"))
        roles = ", ".join(agent.get("roles", []))

    name = f"{first_name} {last_name}".strip()
    team_name = agent.get("source_team_name", "N/A")
    agent_id = agent.get("id", "N/A")

    return f"• {name:<25} | Team: {team_name:<30} | Roles: {roles:<15} | Status: {status:<8} | Email: {email} | Phone: {phone} | ID: {agent_id}"


def main() -> None:
    """Main function to execute the script."""
    api_key = os.getenv("REZEN_API_KEY", "real_Qp1vOeBFiVevF3XV0APgznZ2frPp8fSlaqq7")

    print("ReZEN Your Team Agents")
    print("=" * 80)

    agents = get_my_team_agents(api_key)

    if agents:
        print(f"\n\nSUMMARY: Found {len(agents)} total agents across your teams:")
        print("=" * 80)

        # Group by team for better display
        teams: Dict[str, List[Dict[str, Any]]] = {}
        for agent in agents:
            team_name = agent.get("source_team_name", "Unknown Team")
            if team_name not in teams:
                teams[team_name] = []
            teams[team_name].append(agent)

        for team_name, team_agents in teams.items():
            print(f"\n{team_name} ({len(team_agents)} agents):")
            print("-" * 80)

            for i, agent in enumerate(team_agents, 1):
                print(f"{i:2d}. {format_agent_info(agent)}")

        print("\n" + "=" * 80)
        print(f"Total agents across all your teams: {len(agents)}")

        # Save to JSON file for reference
        with open("my_team_agents.json", "w") as f:
            json.dump(agents, f, indent=2, default=str)
        print("Complete agent data saved to 'my_team_agents.json'")

    else:
        print("No agents found on your teams or unable to retrieve team agent data.")


if __name__ == "__main__":
    main()
