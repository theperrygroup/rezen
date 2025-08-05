#!/usr/bin/env python3
"""
Script to test different endpoints to find where teams data comes from.
"""

import json
import os
from typing import Any, Dict

from rezen.agents import AgentsClient
from rezen.teams import TeamsClient


def test_all_endpoints(api_key: str) -> None:
    """
    Test various endpoints to find team data.

    Args:
        api_key: ReZEN API key for authentication
    """
    agents_client = AgentsClient(api_key=api_key)
    teams_client = TeamsClient(api_key=api_key)

    me = agents_client.get_me()
    agent_id = str(me.get("id"))

    print(
        f"Testing endpoints for agent: {me.get('firstName', '')} {me.get('lastName', '')}"
    )
    print("=" * 80)

    # Test 1: Front line agents (this might contain team info)
    print("\n1. FRONT LINE AGENTS INFO:")
    print("-" * 40)
    try:
        front_line = agents_client.get_front_line_agents_info(agent_id)
        if front_line:
            print(
                "Keys in front line response:",
                (
                    list(front_line.keys())
                    if isinstance(front_line, dict)
                    else "Not a dict"
                ),
            )
            if isinstance(front_line, dict) and "teams" in str(front_line).lower():
                print("CONTAINS TEAMS DATA!")
                print(json.dumps(front_line, indent=2, default=str)[:1000] + "...")
            else:
                print("No teams data found in front line response")
        else:
            print("Empty front line response")
    except Exception as e:
        print(f"Front line error: {str(e)}")

    # Test 2: Try team search with different strategies
    print("\n2. TEAM SEARCH (NO FILTERS):")
    print("-" * 40)
    try:
        all_teams = teams_client.search_teams()
        print(
            "Keys in team search response:",
            list(all_teams.keys()) if isinstance(all_teams, dict) else "Not a dict",
        )
        print(
            f"Team search response: {json.dumps(all_teams, indent=2, default=str)[:500]}..."
        )
    except Exception as e:
        print(f"Team search error: {str(e)}")

    # Test 3: Check if user profile has hidden team references
    print("\n3. USER PROFILE DEEP DIVE:")
    print("-" * 40)
    print("Checking for any team-related keys...")
    for key, value in me.items():
        if "team" in key.lower() or (
            isinstance(value, (dict, list)) and "team" in str(value).lower()
        ):
            print(f"  Found team-related key: {key} = {value}")

    # Test 4: Check downline agents (tiers 1-3)
    print("\n4. DOWNLINE AGENTS (might contain team data):")
    print("-" * 40)
    for tier in [1, 2, 3]:
        try:
            downline = agents_client.get_down_line_agents(agent_id, tier, page_size=5)
            if downline and isinstance(downline, dict):
                content = downline.get("content", [])
                print(f"  Tier {tier}: {len(content)} agents")
                if content and "team" in str(downline).lower():
                    print(f"    TIER {tier} CONTAINS TEAMS DATA!")
                    print(
                        f"    Sample: {json.dumps(downline, indent=2, default=str)[:300]}..."
                    )
                    break
        except Exception as e:
            print(f"  Tier {tier} error: {str(e)}")

    # Test 5: Network size by tier
    print("\n5. NETWORK SIZE BY TIER:")
    print("-" * 40)
    try:
        network = agents_client.get_network_size_by_tier(agent_id)
        print(
            "Network size response keys:",
            list(network.keys()) if isinstance(network, dict) else "Not a dict",
        )
        if "team" in str(network).lower():
            print("NETWORK SIZE CONTAINS TEAMS DATA!")
            print(json.dumps(network, indent=2, default=str)[:500] + "...")
    except Exception as e:
        print(f"Network size error: {str(e)}")


def main() -> None:
    """Main function to execute the test script."""
    api_key = os.getenv("REZEN_API_KEY", "real_Qp1vOeBFiVevF3XV0APgznZ2frPp8fSlaqq7")

    test_all_endpoints(api_key)


if __name__ == "__main__":
    main()
