"""
Rules Arbiter Agent
Handles rule lookups, consistency checking, and edge case resolution
"""

from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class RulesArbiter:
    """Agent for managing D&D rules and ensuring consistency"""
    
    def __init__(self, campaign_data: Dict[str, Any], core_rules: Dict[str, str]):
        """Initialize with campaign-specific and core rules"""
        self.campaign_data = campaign_data
        self.core_rules = core_rules
        self.campaign_name = campaign_data.get("name", "Unknown")
        
        # Extract house rules from campaign
        self.house_rules = self._extract_house_rules()
        
    def _extract_house_rules(self) -> str:
        """Extract house rules content from campaign data"""
        files = self.campaign_data.get("files", {})
        
        # Check for house rules in standard location
        if "houseRules" in files:
            return files["houseRules"]["content"]
        
        # Check for rules in legacy location
        if "rules" in files:
            return files["rules"]["content"]
        
        return ""
    
    def query_rule(self, rule_name: str, context: str = "") -> Dict[str, Any]:
        """Look up a rule and provide guidance"""
        results = {
            "ruleName": rule_name,
            "context": context,
            "coreRule": None,
            "houseRule": None,
            "recommendation": None,
            "sources": []
        }
        
        # Search core rules
        core_result = self._search_in_text(rule_name, self.core_rules.get("house-rules", ""))
        if core_result:
            results["coreRule"] = core_result
            results["sources"].append("Core Rules")
        
        # Search campaign house rules
        house_result = self._search_in_text(rule_name, self.house_rules)
        if house_result:
            results["houseRule"] = house_result
            results["sources"].append(f"{self.campaign_name} House Rules")
        
        # Provide recommendation
        if results["houseRule"]:
            results["recommendation"] = f"Use campaign-specific rule: {results['houseRule'][:200]}..."
        elif results["coreRule"]:
            results["recommendation"] = f"Use core rule: {results['coreRule'][:200]}..."
        else:
            results["recommendation"] = f"No specific rule found for '{rule_name}'. Use standard 5e rules or make a ruling."
        
        return results
    
    def check_house_rules(self, rule_category: Optional[str] = None) -> Dict[str, Any]:
        """Get campaign-specific house rules"""
        if not self.house_rules:
            return {
                "campaign": self.campaign_name,
                "houseRules": "No campaign-specific house rules defined. Using core rules.",
                "categories": []
            }
        
        if rule_category:
            # Search for specific category
            section = self._extract_section(self.house_rules, rule_category)
            return {
                "campaign": self.campaign_name,
                "category": rule_category,
                "rules": section if section else f"No rules found for category: {rule_category}",
                "fullRules": self.house_rules
            }
        
        # Return all house rules
        categories = self._extract_categories(self.house_rules)
        return {
            "campaign": self.campaign_name,
            "houseRules": self.house_rules,
            "categories": categories
        }
    
    def compare_rules(self, rule_name: str) -> Dict[str, Any]:
        """Compare core rules vs campaign house rules"""
        core_search = self._search_in_text(rule_name, self.core_rules.get("house-rules", ""))
        house_search = self._search_in_text(rule_name, self.house_rules)
        
        differences = []
        if core_search and house_search and core_search != house_search:
            differences.append({
                "aspect": rule_name,
                "coreRule": core_search,
                "campaignRule": house_search,
                "useCampaignRule": True
            })
        
        return {
            "ruleName": rule_name,
            "coreDefined": bool(core_search),
            "campaignOverride": bool(house_search),
            "differences": differences,
            "recommendation": "Use campaign rule" if house_search else "Use core rule" if core_search else "Use standard 5e"
        }
    
    def resolve_edge_case(self, situation: str) -> Dict[str, Any]:
        """Suggest a ruling for an unusual situation"""
        # Search for related rules
        keywords = self._extract_keywords(situation)
        related_rules = []
        
        for keyword in keywords:
            core = self._search_in_text(keyword, self.core_rules.get("house-rules", ""))
            house = self._search_in_text(keyword, self.house_rules)
            
            if core:
                related_rules.append({"source": "Core Rules", "keyword": keyword, "text": core[:150]})
            if house:
                related_rules.append({"source": "House Rules", "keyword": keyword, "text": house[:150]})
        
        return {
            "situation": situation,
            "relatedRules": related_rules,
            "suggestion": self._generate_ruling_suggestion(situation, related_rules),
            "note": "This is a suggested ruling. DM has final authority."
        }
    
    def track_ruling(self, ruling: str, session: str, situation: str) -> Dict[str, Any]:
        """Record a session ruling for future consistency"""
        return {
            "recorded": True,
            "session": session,
            "situation": situation,
            "ruling": ruling,
            "note": "Ruling recorded. Consider adding to house rules if it comes up frequently."
        }
    
    def _search_in_text(self, search_term: str, text: str) -> Optional[str]:
        """Search for a term in text and return relevant section"""
        if not text or not search_term:
            return None
        
        # Case-insensitive search
        pattern = re.compile(re.escape(search_term), re.IGNORECASE)
        match = pattern.search(text)
        
        if not match:
            return None
        
        # Get surrounding context (300 chars before and after)
        start = max(0, match.start() - 300)
        end = min(len(text), match.end() + 300)
        
        # Try to break at sentence boundaries
        context = text[start:end]
        
        # Find the start of the first sentence
        first_period = context.find('. ')
        if first_period > 0 and first_period < 100:
            context = context[first_period + 2:]
        
        # Find the end of the last sentence
        last_period = context.rfind('. ')
        if last_period > len(context) - 100:
            context = context[:last_period + 1]
        
        return context.strip()
    
    def _extract_section(self, text: str, section_name: str) -> Optional[str]:
        """Extract a markdown section by heading"""
        # Look for markdown heading
        pattern = re.compile(f"#+\s*{re.escape(section_name)}", re.IGNORECASE)
        match = pattern.search(text)
        
        if not match:
            return None
        
        # Get text until next same-level heading
        start = match.start()
        heading_level = len(re.match(r'#+', text[start:]).group())
        
        # Find next heading of same or higher level
        next_heading = re.compile(f"^#{'{1,' + str(heading_level) + '}'}\s", re.MULTILINE)
        rest_of_text = text[match.end():]
        next_match = next_heading.search(rest_of_text)
        
        if next_match:
            end = match.end() + next_match.start()
        else:
            end = len(text)
        
        return text[start:end].strip()
    
    def _extract_categories(self, text: str) -> List[str]:
        """Extract all markdown heading categories"""
        headings = re.findall(r'^#+\s+(.+)$', text, re.MULTILINE)
        return headings
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from a description"""
        # Common D&D terms to look for
        dnd_terms = [
            "advantage", "disadvantage", "attack", "damage", "spell", "casting",
            "initiative", "combat", "action", "bonus action", "reaction",
            "saving throw", "ability check", "skill check", "critical", "rest",
            "concentration", "death save", "hit points", "armor class"
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for term in dnd_terms:
            if term in text_lower:
                found_keywords.append(term)
        
        # Also extract quoted terms
        quoted = re.findall(r'"([^"]+)"', text)
        found_keywords.extend(quoted[:3])  # Max 3 quoted terms
        
        return found_keywords[:5]  # Return top 5 keywords
    
    def _generate_ruling_suggestion(self, situation: str, related_rules: List[Dict]) -> str:
        """Generate a suggested ruling based on situation and related rules"""
        if not related_rules:
            return "No related rules found. Suggest using standard 5e mechanics or making a balanced ruling that favors narrative over mechanics."
        
        suggestion = "Based on related rules:\n"
        for rule in related_rules[:2]:  # Use top 2 related rules
            suggestion += f"- {rule['source']}: {rule['text']}...\n"
        
        suggestion += "\nSuggested ruling: Apply the principles above to this situation. Favor rulings that keep the game moving and are fair to all players."
        
        return suggestion
