# D&D Campaign MCP Server - Quick Start

## What is This?

An AI-powered assistant for running D&D campaigns! It provides:
- **Rules lookup** - Instant rule checking and house rule management
- **Dice rolling** - Built-in dice roller with advantage/disadvantage
- **Campaign switching** - Manage multiple campaigns easily
- **Consistency checking** - AI agents help maintain campaign coherence

## Installation

### 1. Install Python Dependencies

```powershell
cd w:\personalprojects\DnD(DM)\dnd-mcp
pip install -r requirements.txt
```

### 2. Test the Server

```powershell
python test_campaign_mcp.py
```

You should see:
```
=== D&D MCP Server Test ===
✓ All Tests Passed!
```

### 3. Run the Server (Standalone)

```powershell
python dnd_campaign_mcp.py
```

## Using with Claude Desktop

### Configure Claude Desktop

Add to your Claude Desktop config file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "dnd-campaign": {
      "command": "python",
      "args": [
        "w:\\personalprojects\\DnD(DM)\\dnd-mcp\\dnd_campaign_mcp.py"
      ]
    }
  }
}
```

### Restart Claude Desktop

The MCP server will now be available in Claude!

## Available Tools

### Campaign Management
- `list_campaigns` - See all your campaigns
- `switch_campaign` - Change active campaign
- `get_campaign_info` - Get campaign details

### Rules
- `query_rule` - Look up any D&D rule
- `check_house_rules` - Get campaign house rules
- `compare_rules` - Compare core vs house rules
- `resolve_edge_case` - Get ruling suggestions

### Gameplay
- `roll_dice` - Roll dice (supports advantage/disadvantage)

## Example Usage

In Claude Desktop, you can ask:

```
"What are the rules for advantage?"
"Roll 1d20+5 with advantage for my attack"
"Check the house rules for combat"
"How should I rule this edge case: [situation]"
"Switch to my other campaign"
```

## Playing a Simple Game

Want to test it out? Try this:

1. Ask Claude: **"Let's play a simple D&D encounter. I'm a level 1 fighter."**
2. Claude will use the MCP tools to:
   - Roll dice for you
   - Look up rules
   - Guide the encounter

## Troubleshooting

**Server won't start?**
- Check Python is installed: `python --version`
- Check dependencies: `pip install -r requirements.txt`

**Can't find campaigns?**
- Check `config.json` paths are correct
- Verify `.aiinfo/` folder exists

**Rules not found?**
- Make sure `core-rules/house-rules.md` exists
- Check campaign paths in `config.json`

## Next Steps

1. **Test with a game** - Try the simple D&D encounter!
2. **Add more campaigns** - Use the templates in `campaigns/_templates/`
3. **Customize rules** - Edit `core-rules/house-rules.md`

---

🎲 **Ready to play!**
