# MCP Server Architecture for Multi-Campaign D&D

## Overview

The MCP server provides AI-powered assistance for D&D campaigns through specialized agents that can work with multiple campaigns.

## Design Goals

1. **Campaign-agnostic**: Work with any campaign folder structure
2. **Backwards-compatible**: Support legacy Fragments structure
3. **Agent-based**: Specialized agents for different aspects
4. **Configurable**: Easy to switch between campaigns
5. **Extensible**: Easy to add new agents or campaigns

## Architecture

### Core Components

```
dnd-mcp/
├── server.py                 # Main MCP server
├── config.json              # Campaign configurations
├── agents/                  # AI agent implementations
│   ├── story_guardian.py   # Narrative consistency
│   ├── rules_arbiter.py    # Rules enforcement
│   ├── world_keeper.py     # Lore tracking
│   └── balance_watchdog.py # Game balance
├── campaign_loader.py       # Loads campaign data
├── core/                    # Core functionality
│   ├── file_reader.py      # Read markdown files
│   ├── rule_parser.py      # Parse rule content
│   └── context_builder.py  # Build agent context
└── tools/                   # MCP tools exposed to clients
    ├── query_rules.py
    ├── check_consistency.py
    ├── track_npc.py
    └── session_summary.py
```

### Campaign Configuration

`config.json`:
```json
{
  "activeCampaign": "fragments",
  "campaigns": {
    "fragments": {
      "type": "legacy",
      "name": "Fragments of the First Code",
      "paths": {
        "universe": ".aiinfo/Universe.md",
        "rules": ".aiinfo/Rules.md",
        "characterCreation": ".aiinfo/Fragments_Character_Creation.md",
        "storyIndex": ".aiinfo/Story.index.md",
        "testStories": "test-storylines/",
        "canonStories": "true-story/"
      }
    },
    "campaign-2": {
      "type": "standard",
      "name": "My Next Campaign",
      "path": "campaigns/campaign-2/"
    }
  },
  "coreRulesPath": "core-rules/"
}
```

## Agent System

### Agent Interface

Each agent implements:

```python
class Agent:
    def __init__(self, campaign_data, core_rules):
        """Initialize with campaign and core rules data"""
        
    def check_consistency(self, content, context):
        """Check content against established data"""
        
    def query(self, question, context):
        """Answer questions about the agent's domain"""
        
    def suggest(self, situation):
        """Provide suggestions for the situation"""
```

### Story Guardian Agent

**Responsibilities**:
- Track narrative consistency across sessions
- Monitor character arcs
- Ensure plot threads aren't forgotten
- Suggest story beats

**Data Sources**:
- Session notes (`sessions/*.md`)
- Story files (`story/*.md`)
- Character files (`players/*.md`)
- NPC files (`npcs/*.md`)

**Tools**:
- `check_story_consistency(new_content)` - Verify against existing narrative
- `track_plot_thread(thread_id)` - Get status of plot thread
- `suggest_story_beats(session_number)` - Recommend what to focus on
- `query_character_arc(character_name)` - Get character development status

### Rules Arbiter Agent

**Responsibilities**:
- Ensure consistent rule application
- Resolve rule edge cases
- Track house rules
- Suggest balance adjustments

**Data Sources**:
- Core rules (`core-rules/*.md`)
- Campaign house rules (`house-rules.md`)
- Session rulings (from session notes)

**Tools**:
- `check_rule(rule_name, situation)` - Look up and apply rule
- `resolve_edge_case(situation)` - Suggest ruling for unusual case
- `compare_rules(core_vs_house)` - Show differences
- `track_ruling(ruling, session)` - Record session ruling for consistency

### World Keeper Agent

**Responsibilities**:
- Maintain world consistency
- Track NPC relationships and statuses
- Monitor locations and geography
- Ensure lore coherence

**Data Sources**:
- Universe/world file (`universe.md`)
- NPC files (`npcs/*.md`)
- Session notes (for world changes)
- Resources (maps, etc.)

**Tools**:
- `check_lore_consistency(new_content)` - Verify against universe
- `query_npc(npc_name)` - Get NPC current status
- `track_location(location_name)` - Get location details
- `verify_world_detail(detail)` - Check if detail exists/conflicts

### Balance Watchdog Agent

**Responsibilities**:
- Monitor game balance
- Track player engagement
- Ensure fair spotlight distribution
- Suggest encounter adjustments

**Data Sources**:
- Session notes (player actions, engagement)
- Character files (power levels)
- Encounter notes

**Tools**:
- `assess_balance(session_number)` - Review session balance
- `track_spotlight(player_name)` - Check player involvement
- `suggest_encounter(party_level, type)` - Recommend encounter
- `check_engagement(session_notes)` - Analyze player satisfaction

## MCP Tools (Client-Facing)

These are the tools exposed to the MCP client (Claude, etc.):

### Campaign Management
- `list_campaigns()` - Show available campaigns
- `switch_campaign(campaign_name)` - Change active campaign
- `get_campaign_info(campaign_name)` - Get campaign details

### Rules & Mechanics
- `query_rule(rule_name, context)` - Look up rule
- `check_house_rule(rule_name)` - Get campaign-specific rule
- `resolve_situation(description)` - Get ruling suggestion
- `compare_core_vs_house(rule_name)` - Show rule differences

### Story & Narrative
- `check_story_consistency(content)` - Verify narrative consistency
- `get_plot_threads(status)` - List plot threads (active/resolved/forgotten)
- `track_character_arc(character_name)` - Get character development
- `suggest_next_session(current_session)` - Story suggestions

### World & Lore
- `query_lore(topic)` - Look up world information
- `get_npc_info(npc_name)` - Get NPC details and status
- `check_world_consistency(new_content)` - Verify against universe
- `get_location_info(location_name)` - Get location details

### Session Support
- `generate_session_summary(session_notes)` - Create structured summary
- `track_session(session_number, notes)` - Record session
- `prepare_next_session(session_number)` - Get prep suggestions
- `check_balance(session_number)` - Assess session balance

## Campaign Loader

The `CampaignLoader` class handles reading campaign data:

```python
class CampaignLoader:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        
    def load_campaign(self, campaign_name):
        """Load all data for a campaign"""
        campaign_config = self.config["campaigns"][campaign_name]
        
        if campaign_config["type"] == "legacy":
            return self.load_legacy_campaign(campaign_config)
        else:
            return self.load_standard_campaign(campaign_config)
    
    def load_core_rules(self):
        """Load universal core rules"""
        path = self.config["coreRulesPath"]
        return self.read_markdown_files(path)
        
    def load_legacy_campaign(self, config):
        """Load campaign with custom paths (Fragments)"""
        
    def load_standard_campaign(self, config):
        """Load campaign from standard folder structure"""
```

## Implementation Plan

### Phase 1: Core Infrastructure
1. Campaign loader with config system
2. File readers for markdown
3. Basic MCP server setup

### Phase 2: Rules Arbiter Agent
4. Core rules parser
5. House rules integration
6. Rule query tools

### Phase 3: World Keeper Agent
7. Universe/lore parser
8. NPC tracking
9. Consistency checking

### Phase 4: Story Guardian Agent
10. Session notes parser
11. Plot thread tracking
12. Character arc monitoring

### Phase 5: Balance Watchdog Agent
13. Engagement analysis
14. Balance suggestions
15. Encounter recommendations

## Next Steps

1. Update `dnd-mcp/config.json` with campaign configurations
2. Implement `CampaignLoader` class
3. Create basic agent framework
4. Implement Rules Arbiter first (most useful immediately)
5. Add other agents incrementally

---

**Ready to start implementation!** 🚀
