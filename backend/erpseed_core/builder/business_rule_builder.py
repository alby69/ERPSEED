"""
Business Rule Builder - Creates business rules
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class Action:
    """Represents a business rule action"""
    type: str
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Condition:
    """Represents a business rule condition"""
    field: str
    operator: str
    value: Any = None


@dataclass
class BusinessRule:
    """Represents a business rule"""
    name: str
    technical_name: str
    model: str
    type: str
    title: str = ""
    description: str = ""
    conditions: List[Condition] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    trigger: str = "on_save"
    priority: int = 0
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)


class BusinessRuleBuilder:
    """Builds business rules from JSON configuration"""
    
    def __init__(self):
        self.rules: Dict[str, BusinessRule] = {}
    
    def build(self, data: Dict[str, Any]) -> BusinessRule:
        """Build a business rule from JSON data"""
        conditions = []
        for cond_data in data.get("conditions", []):
            cond = Condition(
                field=cond_data["field"],
                operator=cond_data.get("operator", "=="),
                value=cond_data.get("value"),
            )
            conditions.append(cond)
        
        actions = []
        for action_data in data.get("actions", []):
            action = Action(
                type=action_data["type"],
                params=action_data.get("params", {}),
            )
            actions.append(action)
        
        rule = BusinessRule(
            name=data["name"],
            technical_name=data["technical_name"],
            model=data["model"],
            type=data.get("type", "validation"),
            title=data.get("title", data["name"]),
            description=data.get("description", ""),
            conditions=conditions,
            actions=actions,
            trigger=data.get("trigger", "on_save"),
            priority=data.get("priority", 0),
            enabled=data.get("enabled", True),
            settings=data.get("settings", {}),
        )
        
        self.rules[rule.technical_name] = rule
        return rule
    
    def get_rule(self, technical_name: str) -> Optional[BusinessRule]:
        """Get a business rule by technical name"""
        return self.rules.get(technical_name)
    
    def list_rules(self) -> List[BusinessRule]:
        """List all built business rules"""
        return list(self.rules.values())
    
    def to_dict(self, rule: BusinessRule) -> Dict[str, Any]:
        """Convert business rule to dictionary"""
        return {
            "name": rule.name,
            "technical_name": rule.technical_name,
            "model": rule.model,
            "type": rule.type,
            "title": rule.title,
            "description": rule.description,
            "conditions": [
                {
                    "field": c.field,
                    "operator": c.operator,
                    "value": c.value,
                }
                for c in rule.conditions
            ],
            "actions": [
                {
                    "type": a.type,
                    "params": a.params,
                }
                for a in rule.actions
            ],
            "trigger": rule.trigger,
            "priority": rule.priority,
            "enabled": rule.enabled,
            "settings": rule.settings,
        }
