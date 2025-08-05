#!/usr/bin/env python3
"""
Script to get and display all agents on your teams using the sponsor tree API.
"""

import json
import os
from typing import Any, Dict, List

from rezen.agents import AgentsClient


def get_team_agents_from_sponsor_tree(api_key: str) -> List[Dict[str, Any]]:
    """
    Get all team agents from the sponsor tree API.

    Args:
        api_key: ReZEN API key for authentication

    Returns:
        List of all agents from all teams in the sponsor tree
    """
    client = AgentsClient(api_key=api_key)

    try:
        # Get current user info
        me = client.get_me()
        agent_id = str(me.get("id"))

        print(
            f"Getting sponsor tree for agent: {me.get('firstName', '')} {me.get('lastName', '')} ({agent_id})"
        )

        # Get sponsor tree which contains team information
        sponsor_tree = client.get_sponsor_tree(agent_id)

        all_agents = []
        team_summary = []

        # Extract teams from sponsor tree
        if "teams" in sponsor_tree:
            teams = sponsor_tree["teams"]

            for team in teams:
                team_id = team.get("id", "Unknown")
                team_name = team.get("name", "Unknown Team")
                team_type = team.get("type", "Unknown")
                team_status = team.get("status", "Unknown")

                agents_in_team = team.get("agents", [])

                team_info = {
                    "team_id": team_id,
                    "team_name": team_name,
                    "team_type": team_type,
                    "team_status": team_status,
                    "agent_count": len(agents_in_team),
                }
                team_summary.append(team_info)

                # Add team info to each agent
                for agent_member in agents_in_team:
                    agent_data = agent_member.get("agent", {})

                    # Enhanced agent info with team context
                    enhanced_agent = {
                        "id": agent_member.get("id"),
                        "agent_id": agent_data.get("id"),
                        "firstName": agent_data.get("firstName", ""),
                        "lastName": agent_data.get("lastName", ""),
                        "emailAddress": agent_data.get("emailAddress"),
                        "phoneNumber": agent_data.get("phoneNumber"),
                        "agentStatus": agent_data.get("agentStatus", "Unknown"),
                        "team_id": team_id,
                        "team_name": team_name,
                        "team_type": team_type,
                        "roles": agent_member.get("roles", []),
                        "flexRoles": agent_member.get("flexRoles", []),
                        "avatar": agent_data.get("avatar"),
                        "joinDate": agent_data.get("joinDate"),
                        "anniversaryDate": agent_data.get("anniversaryDate"),
                    }
                    all_agents.append(enhanced_agent)

        print(f"\nTeam Summary:")
        print("=" * 60)
        for team in team_summary:
            print(f"• {team['team_name']} ({team['team_type']})")
            print(f"  ID: {team['team_id']}")
            print(f"  Status: {team['team_status']}")
            print(f"  Agents: {team['agent_count']}")
            print()

        return all_agents

    except Exception as e:
        print(f"Error getting sponsor tree: {str(e)}")
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
    email = agent.get("emailAddress", "N/A")
    phone = agent.get("phoneNumber", "N/A")
    status = agent.get("agentStatus", "N/A")
    roles = ", ".join(agent.get("roles", []))
    team_name = agent.get("team_name", "N/A")
    agent_id = agent.get("id", "N/A")

    return f"• {name:<25} | Team: {team_name:<20} | Roles: {roles:<15} | Status: {status:<8} | Email: {email} | Phone: {phone} | ID: {agent_id}"


def main() -> None:
    """Main function to execute the script."""
    api_key = os.getenv("REZEN_API_KEY", "real_Qp1vOeBFiVevF3XV0APgznZ2frPp8fSlaqq7")

    print("ReZEN Team Agents (via Sponsor Tree)")
    print("=" * 80)

    agents = get_team_agents_from_sponsor_tree(api_key)

    if agents:
        print(f"Found {len(agents)} total agents across all teams:")
        print("=" * 80)

        # Group by team for better display
        teams: Dict[str, List[Dict[str, Any]]] = {}
        for agent in agents:
            team_name = agent.get("team_name", "Unknown Team")
            if team_name not in teams:
                teams[team_name] = []
            teams[team_name].append(agent)

        for team_name, team_agents in teams.items():
            print(f"\n{team_name} ({len(team_agents)} agents):")
            print("-" * 60)

            for i, agent in enumerate(team_agents, 1):
                print(f"{i:2d}. {format_agent_info(agent)}")

        print("\n" + "=" * 80)
        print(f"Total agents across all teams: {len(agents)}")

        # Save to JSON file for reference
        with open("all_team_agents.json", "w") as f:
            json.dump(agents, f, indent=2, default=str)
        print("Complete agent data saved to 'all_team_agents.json'")

    else:
        print("No team agents found or unable to retrieve team agent data.")


if __name__ == "__main__":
    main()
