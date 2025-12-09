"""
D&D MCP Server - Main Entry Point
Provides AI assistance for D&D campaigns through MCP protocol
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from campaign_loader import CampaignLoader
from agents.rules_arbiter import RulesArbiter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dnd-mcp")

# Initialize server
app = Server("dnd-campaign-mcp")

# Global state
campaign_loader = None
current_campaign = None
core_rules = None
rules_arbiter = None


async def initialize_server():
    """Initialize the server and load campaign data"""
    global campaign_loader, current_campaign, core_rules, rules_arbiter
    
    logger.info("Initializing D&D Campaign MCP Server...")
    
    # Load configuration and campaign
    campaign_loader = CampaignLoader("config.json")
    core_rules = campaign_loader.load_core_rules()
    current_campaign = campaign_loader.load_campaign()
    
    # Initialize agents
    rules_arbiter = RulesArbiter(current_campaign, core_rules)
    
    logger.info(f"Loaded campaign: {current_campaign['name']}")
    logger.info("Server ready!")


# =======================
# Campaign Management Tools
# =======================

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available MCP tools"""
    return [
        # Campaign Management
        types.Tool(
            name="list_campaigns",
            description="List all available D&D campaigns",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="switch_campaign",
            description="Switch to a different campaign",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {
                        "type": "string",
                        "description": "Name of the campaign to switch to"
                    }
                },
                "required": ["campaign_name"]
            }
        ),
        types.Tool(
            name="get_campaign_info",
            description="Get information about a campaign",
            inputSchema={
                "type": "object",
                "properties": {
                    "campaign_name": {
                        "type": "string",
                        "description": "Name of the campaign (optional, defaults to active campaign)"
                    }
                },
                "required": []
            }
        ),
        
        # Rules Arbiter Tools
        types.Tool(
            name="query_rule",
            description="Look up a D&D rule (checks both core rules and campaign house rules)",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_name": {
                        "type": "string",
                        "description": "The rule or mechanic to look up (e.g., 'advantage', 'spell slots', 'death saves')"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional context about the situation"
                    }
                },
                "required": ["rule_name"]
            }
        ),
        types.Tool(
            name="check_house_rules",
            description="Get campaign-specific house rules",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional category to filter (e.g., 'Combat', 'Magic', 'Character Creation')"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="compare_rules",
            description="Compare core rules vs campaign house rules for a specific mechanic",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_name": {
                        "type": "string",
                        "description": "The rule to compare"
                    }
                },
                "required": ["rule_name"]
            }
        ),
        types.Tool(
            name="resolve_edge_case",
            description="Get a suggested ruling for an unusual situation not covered by existing rules",
            inputSchema={
                "type": "object",
                "properties": {
                    "situation": {
                        "type": "string",
                        "description": "Description of the edge case or unusual situation"
                    }
                },
                "required": ["situation"]
            }
        ),
        
        # Gameplay Tools
        types.Tool(
            name="roll_dice",
            description="Roll dice for D&D (e.g., '1d20+5', '2d6', '1d20' for advantage/disadvantage)",
            inputSchema={
                "type": "object",
                "properties": {
                    "dice_expression": {
                        "type": "string",
                        "description": "Dice to roll (e.g., '1d20+5', '2d6', '3d8+2')"
                    },
                    "advantage": {
                        "type": "boolean",
                        "description": "Roll with advantage (roll twice, take higher)"
                    },
                    "disadvantage": {
                        "type": "boolean",
                        "description": "Roll with disadvantage (roll twice, take lower)"
                    },
                    "description": {
                        "type": "string",
                        "description": "What the roll is for (e.g., 'Attack roll', 'Stealth check')"
                    }
                },
                "required": ["dice_expression"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    
    try:
        # Campaign Management
        if name == "list_campaigns":
            campaigns = campaign_loader.list_campaigns()
            result = "# Available Campaigns\n\n"
            for camp in campaigns:
                active = "✓ ACTIVE" if camp["active"] else ""
                result += f"## {camp['displayName']} {active}\n"
                result += f"- **ID**: {camp['name']}\n"
                result += f"- **Type**: {camp['type']}\n"
                result += f"- **Description**: {camp['description']}\n\n"
            return [types.TextContent(type="text", text=result)]
        
        elif name == "switch_campaign":
            campaign_name = arguments["campaign_name"]
            success = campaign_loader.switch_campaign(campaign_name)
            if success:
                # Reload campaign data and agents
                global current_campaign, rules_arbiter
                current_campaign = campaign_loader.load_campaign()
                rules_arbiter = RulesArbiter(current_campaign, core_rules)
                
                return [types.TextContent(
                    type="text",
                    text=f"✓ Switched to campaign: {current_campaign['name']}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"✗ Campaign not found: {campaign_name}"
                )]
        
        elif name == "get_campaign_info":
            campaign_name = arguments.get("campaign_name")
            info = campaign_loader.get_campaign_info(campaign_name)
            result = f"# {info['displayName']}\n\n"
            result += f"- **ID**: {info['name']}\n"
            result += f"- **Type**: {info['type']}\n"
            result += f"- **Description**: {info['description']}\n"
            result += f"- **Status**: {'ACTIVE' if info['active'] else 'Inactive'}\n"
            return [types.TextContent(type="text", text=result)]
        
        # Rules Arbiter Tools
        elif name == "query_rule":
            rule_name = arguments["rule_name"]
            context = arguments.get("context", "")
            result = rules_arbiter.query_rule(rule_name, context)
            
            output = f"# Rule: {result['ruleName']}\n\n"
            
            if result['houseRule']:
                output += "## Campaign House Rule\n"
                output += f"{result['houseRule']}\n\n"
            
            if result['coreRule']:
                output += "## Core Rule\n"
                output += f"{result['coreRule']}\n\n"
            
            output += "## Recommendation\n"
            output += f"{result['recommendation']}\n"
            
            return [types.TextContent(type="text", text=output)]
        
        elif name == "check_house_rules":
            category = arguments.get("category")
            result = rules_arbiter.check_house_rules(category)
            
            output = f"# House Rules: {result['campaign']}\n\n"
            
            if category:
                output += f"## Category: {category}\n\n"
                output += result['rules']
            else:
                output += result['houseRules']
            
            return [types.TextContent(type="text", text=output)]
        
        elif name == "compare_rules":
            rule_name = arguments["rule_name"]
            result = rules_arbiter.compare_rules(rule_name)
            
            output = f"# Rule Comparison: {result['ruleName']}\n\n"
            output += f"**Recommendation**: {result['recommendation']}\n\n"
            
            if result['differences']:
                for diff in result['differences']:
                    output += f"## Core Rule\n{diff['coreRule']}\n\n"
                    output += f"## Campaign Rule\n{diff['campaignRule']}\n\n"
            else:
                output += "No differences found between core and campaign rules.\n"
            
            return [types.TextContent(type="text", text=output)]
        
        elif name == "resolve_edge_case":
            situation = arguments["situation"]
            result = rules_arbiter.resolve_edge_case(situation)
            
            output = f"# Edge Case Ruling\n\n"
            output += f"**Situation**: {result['situation']}\n\n"
            
            if result['relatedRules']:
                output += "## Related Rules\n\n"
                for rule in result['relatedRules']:
                    output += f"**{rule['source']}** ({rule['keyword']}): {rule['text']}\n\n"
            
            output += "## Suggested Ruling\n\n"
            output += f"{result['suggestion']}\n\n"
            output += f"*{result['note']}*\n"
            
            return [types.TextContent(type="text", text=output)]
        
        # Dice Rolling
        elif name == "roll_dice":
            import random
            import re
            
            dice_expr = arguments["dice_expression"]
            advantage = arguments.get("advantage", False)
            disadvantage = arguments.get("disadvantage", False)
            description = arguments.get("description", "")
            
            # Parse dice expression (e.g., "2d6+3")
            match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dice_expr)
            if not match:
                return [types.TextContent(
                    type="text",
                    text=f"Invalid dice expression: {dice_expr}. Use format like '1d20+5' or '2d6'"
                )]
            
            num_dice = int(match.group(1))
            die_size = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0
            
            # Roll dice
            def roll():
                rolls = [random.randint(1, die_size) for _ in range(num_dice)]
                return rolls, sum(rolls) + modifier
            
            if advantage or disadvantage:
                rolls1, total1 = roll()
                rolls2, total2 = roll()
                
                if advantage:
                    final_rolls, final_total = (rolls1, total1) if total1 > total2 else (rolls2, total2)
                    adv_text = "ADVANTAGE"
                else:
                    final_rolls, final_total = (rolls1, total1) if total1 < total2 else (rolls2, total2)
                    adv_text = "DISADVANTAGE"
                
                output = f"# 🎲 Dice Roll: {dice_expr} ({adv_text})\n\n"
                if description:
                    output += f"**For**: {description}\n\n"
                output += f"**Roll 1**: {rolls1} = {total1}\n"
                output += f"**Roll 2**: {rolls2} = {total2}\n\n"
                output += f"**Final Result**: **{final_total}**\n"
            else:
                rolls, total = roll()
                output = f"# 🎲 Dice Roll: {dice_expr}\n\n"
                if description:
                    output += f"**For**: {description}\n\n"
                output += f"**Rolls**: {rolls}\n"
                if modifier != 0:
                    output += f"**Modifier**: {modifier:+d}\n"
                output += f"\n**Total**: **{total}**\n"
            
            return [types.TextContent(type="text", text=output)]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Main entry point"""
    await initialize_server()
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
