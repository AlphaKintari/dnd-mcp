"""
Campaign Loader for D&D MCP Server
Loads campaign data from various folder structures
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class CampaignLoader:
    """Loads and manages campaign data for the MCP server"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the campaign loader with configuration"""
        self.config_path = Path(config_path)
        self.base_path = self.config_path.parent
        self.config = self._load_config()
        self.active_campaign_name = self.config.get("activeCampaign", "fragments")
        
    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    def list_campaigns(self) -> List[Dict[str, str]]:
        """List all available campaigns"""
        campaigns = []
        for name, config in self.config["campaigns"].items():
            campaigns.append({
                "name": name,
                "displayName": config["name"],
                "description": config.get("description", ""),
                "type": config["type"],
                "active": name == self.active_campaign_name
            })
        return campaigns
    
    def switch_campaign(self, campaign_name: str) -> bool:
        """Switch the active campaign"""
        if campaign_name not in self.config["campaigns"]:
            logger.error(f"Campaign not found: {campaign_name}")
            return False
        
        self.active_campaign_name = campaign_name
        self.config["activeCampaign"] = campaign_name
        
        # Save updated config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
        
        logger.info(f"Switched to campaign: {campaign_name}")
        return True
    
    def load_campaign(self, campaign_name: Optional[str] = None) -> Dict[str, Any]:
        """Load all data for a campaign"""
        name = campaign_name or self.active_campaign_name
        
        if name not in self.config["campaigns"]:
            raise ValueError(f"Campaign not found: {name}")
        
        campaign_config = self.config["campaigns"][name]
        
        if campaign_config["type"] == "legacy":
            return self._load_legacy_campaign(campaign_config)
        else:
            return self._load_standard_campaign(campaign_config)
    
    def load_core_rules(self) -> Dict[str, str]:
        """Load universal core rules"""
        core_path = self.base_path / self.config["coreRulesPath"]
        
        rules = {}
        if core_path.exists():
            for file_path in core_path.glob("*.md"):
                content = self._read_file(file_path)
                if content:
                    rules[file_path.stem] = content
        
        return rules
    
    def _load_legacy_campaign(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load campaign with custom paths (like Fragments)"""
        campaign_data = {
            "name": config["name"],
            "description": config.get("description", ""),
            "type": "legacy",
            "files": {}
        }
        
        # Load each specified file
        for key, relative_path in config["paths"].items():
            full_path = self.base_path / relative_path
            
            if full_path.is_file():
                content = self._read_file(full_path)
                if content:
                    campaign_data["files"][key] = {
                        "path": str(full_path),
                        "content": content
                    }
            elif full_path.is_dir():
                # Load all markdown files from directory
                files = {}
                for file_path in full_path.rglob("*.md"):
                    content = self._read_file(file_path)
                    if content:
                        relative = file_path.relative_to(full_path)
                        files[str(relative)] = {
                            "path": str(file_path),
                            "content": content
                        }
                campaign_data["files"][key] = files
        
        return campaign_data
    
    def _load_standard_campaign(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load campaign from standard folder structure"""
        campaign_path = self.base_path / config["path"]
        
        campaign_data = {
            "name": config["name"],
            "description": config.get("description", ""),
            "type": "standard",
            "files": {}
        }
        
        # Standard file structure
        standard_files = {
            "info": "campaign-info.md",
            "universe": "universe.md",
            "houseRules": "house-rules.md"
        }
        
        for key, filename in standard_files.items():
            file_path = campaign_path / filename
            if file_path.exists():
                content = self._read_file(file_path)
                if content:
                    campaign_data["files"][key] = {
                        "path": str(file_path),
                        "content": content
                    }
        
        # Load directories
        directories = {
            "npcs": "npcs",
            "sessions": "sessions",
            "players": "players",
            "story": "story",
            "resources": "resources"
        }
        
        for key, dirname in directories.items():
            dir_path = campaign_path / dirname
            if dir_path.exists():
                files = {}
                for file_path in dir_path.rglob("*.md"):
                    content = self._read_file(file_path)
                    if content:
                        relative = file_path.relative_to(dir_path)
                        files[str(relative)] = {
                            "path": str(file_path),
                            "content": content
                        }
                if files:
                    campaign_data["files"][key] = files
        
        return campaign_data
    
    def _read_file(self, file_path: Path) -> Optional[str]:
        """Read a file and return its contents"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return None
    
    def get_campaign_info(self, campaign_name: Optional[str] = None) -> Dict[str, Any]:
        """Get basic information about a campaign without loading all data"""
        name = campaign_name or self.active_campaign_name
        
        if name not in self.config["campaigns"]:
            raise ValueError(f"Campaign not found: {name}")
        
        config = self.config["campaigns"][name]
        return {
            "name": name,
            "displayName": config["name"],
            "description": config.get("description", ""),
            "type": config["type"],
            "active": name == self.active_campaign_name
        }
