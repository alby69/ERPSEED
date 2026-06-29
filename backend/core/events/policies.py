"""
Agent Governance & Policy Layer
Defines and enforces rules for Agent capabilities.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class Policy:
    """Defines a rule for capability execution."""
    name: str
    description: str
    capability_pattern: str  # e.g., "confirm_*"
    effect: str = "allow"    # "allow" or "deny"
    conditions: List[Dict[str, Any]] = field(default_factory=list)
    require_approval: bool = False
    rate_limit: Optional[int] = None  # calls per hour

class PolicyEngine:
    """Enforces policies on capability execution."""

    def __init__(self):
        self._policies: List[Policy] = []
        self._execution_log: List[Dict[str, Any]] = []

    def add_policy(self, policy: Policy):
        self._policies.append(policy)
        logger.info(f"Added policy: {policy.name}")

    def check_access(self, capability_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Checks if a capability can be executed in the given context.
        Returns a dict with 'allowed', 'reason', and 'require_approval'.
        """
        import re

        result = {
            "allowed": True,
            "reason": "No policies matched, defaulting to allow",
            "require_approval": False
        }

        matched_policies = []
        for policy in self._policies:
            # Simple glob-like pattern matching
            pattern = policy.capability_pattern.replace('*', '.*')
            if re.match(f"^{pattern}$", capability_name):
                matched_policies.append(policy)

        if not matched_policies:
            return result

        # Apply policies (last one wins for simplicity, or first 'deny')
        for policy in matched_policies:
            if policy.effect == "deny":
                return {
                    "allowed": False,
                    "reason": f"Denied by policy: {policy.name}",
                    "require_approval": False
                }

            if policy.require_approval:
                result["require_approval"] = True
                result["reason"] = f"Approval required by policy: {policy.name}"

        return result

    def log_execution(self, capability_name: str, context: Dict[str, Any], success: bool):
        self._execution_log.append({
            "capability": capability_name,
            "timestamp": datetime.utcnow(),
            "tenant_id": context.get("tenant_id"),
            "success": success
        })

# Global singleton
policy_engine = PolicyEngine()

# Pre-defined system policies
policy_engine.add_policy(Policy(
    name="Safe Sales Confirmation",
    description="Requires approval for confirming sales orders",
    capability_pattern="confirm_sales_order",
    require_approval=True
))

policy_engine.add_policy(Policy(
    name="Protect HR Records",
    description="Require approval for new employee creation",
    capability_pattern="create_employee",
    require_approval=True
))
