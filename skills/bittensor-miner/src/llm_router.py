"""
LLM Router
Intelligent task triage and LLM selection.
Phase 1: Basic routing rules.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class LLMRouter:
    """
    Routes tasks to appropriate LLM APIs based on task characteristics.
    Phase 1: Simple rule-based routing.
    """

    def __init__(self, profile_path: str = "config/subnet-profiles.json"):
        self.profile_path = Path(profile_path)
        self.profiles = self._load_profiles()
        logger.debug("LLMRouter initialized")

    def _load_profiles(self) -> Dict[str, Any]:
        """Load subnet profiles"""
        try:
            with open(self.profile_path, 'r') as f:
                profiles = json.load(f)
            return profiles
        except FileNotFoundError:
            logger.warning(f"Subnet profiles not found: {self.profile_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid profiles JSON: {e}")
            return {}

    def select_llm(self, task_type: str = 'generation',
                   reasoning_depth: str = 'medium',
                   subnet_id: int = 1) -> Dict[str, Any]:
        """
        Select best LLM for a task.
        Phase 1: Simple decision tree.

        Args:
            task_type: Type of task (generation, evaluation, ranking)
            reasoning_depth: Reasoning complexity (simple, medium, complex)
            subnet_id: Target subnet

        Returns:
            LLM configuration dict
        """
        # Get subnet preference
        subnet = self.profiles.get('subnets', {}).get(str(subnet_id), {})
        preferred_llm = subnet.get('preferred_llm', 'openai-gpt4')

        # Basic routing logic
        if reasoning_depth == 'complex':
            # Complex reasoning prefers Claude
            selected_llm = 'claude-sonnet'
        elif task_type == 'generation' and reasoning_depth == 'simple':
            # Fast generation prefers Gemini
            selected_llm = 'gemini-pro'
        else:
            # Default to subnet preference
            selected_llm = preferred_llm

        config = {
            'model': selected_llm,
            'provider': self._get_provider(selected_llm),
            'max_tokens': subnet.get('max_tokens_per_task', 1000),
            'temperature': 0.7,
        }

        logger.debug(f"Selected LLM {selected_llm} for {task_type}/{reasoning_depth}")
        return config

    def _get_provider(self, model_name: str) -> str:
        """Get provider for a model"""
        if 'gpt' in model_name.lower():
            return 'openai'
        elif 'claude' in model_name.lower():
            return 'anthropic'
        elif 'gemini' in model_name.lower():
            return 'google'
        return 'openai'  # Default

    def should_respond(self, task: Dict[str, Any],
                       subnet_id: int = 1,
                       current_budget_percent: float = 50.0) -> bool:
        """
        Determine if we should respond to a task.
        Phase 1: Simple threshold-based decision.

        Args:
            task: Task data
            subnet_id: Target subnet
            current_budget_percent: Current budget utilization (0-100)

        Returns:
            True if should respond, False otherwise
        """
        # Check budget threshold
        if current_budget_percent > 90:
            logger.warning("Budget too low, skipping task")
            return False

        # Get subnet profile
        subnet = self.profiles.get('subnets', {}).get(str(subnet_id), {})

        # Check confidence threshold
        classification = task.get('classification', {})
        confidence = classification.get('confidence', 0.5)
        min_threshold = subnet.get('min_confidence_threshold', 0.5)

        if confidence < min_threshold:
            logger.debug(f"Confidence {confidence} below threshold {min_threshold}")
            return False

        # Check participation rate
        participation_rate = subnet.get('participation_rate', 1.0)
        import random
        if random.random() > participation_rate:
            logger.debug(f"Participation rate check failed")
            return False

        return True

    def allocate_tokens(self, task: Dict[str, Any],
                        llm_config: Dict[str, Any],
                        remaining_budget: int) -> int:
        """
        Allocate token budget for a task.
        Phase 1: Simple allocation.

        Args:
            task: Task data
            llm_config: LLM configuration
            remaining_budget: Remaining tokens available

        Returns:
            Allocated tokens for this task
        """
        max_tokens = llm_config.get('max_tokens', 1000)

        # Ensure we have budget
        if remaining_budget < max_tokens:
            # Use what's available (already checked we have minimum)
            return int(remaining_budget * 0.9)  # Keep 10% buffer

        return max_tokens

    def get_best_strategy(self, task_type: str) -> str:
        """
        Get best prompt strategy for task type.
        Phase 1: Simple mapping.

        Args:
            task_type: Type of task

        Returns:
            Strategy name
        """
        if task_type in ['evaluation', 'ranking']:
            return 'structured_reasoning'
        elif task_type == 'generation':
            return 'concise_generation'
        else:
            return 'structured_reasoning'
