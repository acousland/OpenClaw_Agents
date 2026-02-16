"""Token budget tracking and management for LLM APIs"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class TokenBudgetManager:
    """Manages token budgets for multiple LLM API providers"""

    def __init__(self, config_path: str = "config/token-budgets.json"):
        self.config_path = Path(config_path)
        self.budgets = {}
        self.load_budgets()

    def load_budgets(self) -> None:
        """Load budget configuration from JSON file"""
        if not self.config_path.exists():
            logger.warning(f"Budget config not found at {self.config_path}")
            return

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            self.budgets = config.get('budgets', {})
            logger.info(f"Loaded budgets for {len(self.budgets)} LLM providers")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse budget config: {e}")
            raise

    def save_budgets(self) -> None:
        """Save budget configuration back to JSON file"""
        try:
            config = {
                'budgets': self.budgets,
                'last_updated': datetime.utcnow().isoformat()
            }
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.debug("Budgets saved")
        except Exception as e:
            logger.error(f"Failed to save budgets: {e}")
            raise

    def get_remaining_budget(self, api_name: str) -> int:
        """Get remaining monthly budget tokens for an API"""
        if api_name not in self.budgets:
            logger.warning(f"Unknown API: {api_name}")
            return 0

        budget_info = self.budgets[api_name]
        monthly = budget_info.get('monthly_allowance', 0)
        used = budget_info.get('used_this_month', 0)
        return max(0, monthly - used)

    def can_spend_tokens(self, api_name: str, tokens_needed: int,
                         min_threshold_percent: float = 0.1) -> bool:
        """
        Check if we have enough budget to spend tokens.

        Args:
            api_name: Name of the LLM API
            tokens_needed: Number of tokens needed
            min_threshold_percent: Minimum percentage of budget to keep as buffer (0-1)

        Returns:
            True if budget is sufficient, False otherwise
        """
        if api_name not in self.budgets:
            logger.warning(f"Unknown API: {api_name}")
            return False

        budget_info = self.budgets[api_name]
        monthly = budget_info.get('monthly_allowance', 0)
        used = budget_info.get('used_this_month', 0)
        remaining = monthly - used

        # Apply minimum threshold
        safe_spend = monthly * (1.0 - min_threshold_percent)
        can_afford = (used + tokens_needed) <= safe_spend

        if not can_afford:
            logger.warning(
                f"Insufficient budget for {api_name}: "
                f"need {tokens_needed}, have {remaining} "
                f"(keeping {min_threshold_percent*100}% buffer)"
            )
        return can_afford

    def record_token_spend(self, api_name: str, tokens_spent: int) -> None:
        """Record token spending for an API"""
        if api_name not in self.budgets:
            logger.warning(f"Unknown API: {api_name}")
            return

        self.budgets[api_name]['used_this_month'] += tokens_spent
        logger.debug(f"Recorded {tokens_spent} tokens for {api_name}")
        self.save_budgets()

    def get_budget_info(self, api_name: str) -> Optional[Dict]:
        """Get full budget information for an API"""
        return self.budgets.get(api_name)

    def get_all_budgets(self) -> Dict:
        """Get all budget information"""
        return self.budgets.copy()

    def reset_monthly_budgets(self) -> None:
        """Reset monthly usage counters (call on first day of month)"""
        for api_name in self.budgets:
            self.budgets[api_name]['used_this_month'] = 0
        self.save_budgets()
        logger.info("Monthly budgets reset")

    def get_budget_utilization_percent(self, api_name: str) -> float:
        """Get budget utilization as percentage (0-100)"""
        if api_name not in self.budgets:
            return 0.0

        budget_info = self.budgets[api_name]
        monthly = budget_info.get('monthly_allowance', 1)  # Avoid divide by zero
        used = budget_info.get('used_this_month', 0)

        return (used / monthly) * 100 if monthly > 0 else 100.0

    def get_daily_limit_remaining(self, api_name: str) -> int:
        """Get remaining daily token limit (simplified - doesn't track per-day)"""
        if api_name not in self.budgets:
            return 0

        budget_info = self.budgets[api_name]
        return budget_info.get('daily_limit', 0)
