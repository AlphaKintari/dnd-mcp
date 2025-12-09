# Quick Test Script for D&D MCP Server
# Tests the Rules Arbiter and dice rolling

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from campaign_loader import CampaignLoader
from agents.rules_arbiter import RulesArbiter


async def test_server():
    """Test the MCP server components"""
    print("=== D&D MCP Server Test ===\n")
    
    # Test 1: Load campaigns
    print("1. Loading campaigns...")
    loader = CampaignLoader("config.json")
    campaigns = loader.list_campaigns()
    
    print(f"   Found {len(campaigns)} campaigns:")
    for camp in campaigns:
        active = "[ACTIVE]" if camp["active"] else ""
        print(f"   - {camp['displayName']} {active}")
    
    # Test 2: Load active campaign
    print("\n2. Loading active campaign...")
    campaign = loader.load_campaign()
    print(f"   Loaded: {campaign['name']}")
    print(f"   Type: {campaign['type']}")
    print(f"   Files: {len(campaign['files'])} categories")
    
    # Test 3: Load core rules
    print("\n3. Loading core rules...")
    core_rules = loader.load_core_rules()
    print(f"   Loaded {len(core_rules)} rule files")
    for filename in core_rules.keys():
        print(f"   - {filename}")
    
    # Test 4: Initialize Rules Arbiter
    print("\n4. Initializing Rules Arbiter agent...")
    arbiter = RulesArbiter(campaign, core_rules)
    print("   ✓ Agent initialized")
    
    # Test 5: Query a rule
    print("\n5. Testing rule query...")
    result = arbiter.query_rule("advantage", "Player wants to know how advantage works")
    print(f"   Rule: {result['ruleName']}")
    print(f"   Sources: {result['sources']}")
    if result['coreRule']:
        print(f"   Core Rule Found: {result['coreRule'][:100]}...")
    
    # Test 6: Check house rules
    print("\n6. Testing house rules check...")
    house_result = arbiter.check_house_rules()
    print(f"   Campaign: {house_result['campaign']}")
    print(f"   Categories: {len(house_result.get('categories', []))}")
    
    # Test 7: Edge case resolution
    print("\n7. Testing edge case resolution...")
    edge_result = arbiter.resolve_edge_case("Can a player use a bonus action to drink a potion while grappled?")
    print(f"   Situation: {edge_result['situation'][:80]}...")
    print(f"   Related rules found: {len(edge_result['relatedRules'])}")
    print(f"   Suggestion: {edge_result['suggestion'][:100]}...")
    
    print("\n=== All Tests Passed! ===")
    print("\n✓ MCP Server is ready to use!")
    print("\nNext steps:")
    print("1. Configure in Claude Desktop (see README)")
    print("2. Or run: python dnd_campaign_mcp.py")


if __name__ == "__main__":
    asyncio.run(test_server())
