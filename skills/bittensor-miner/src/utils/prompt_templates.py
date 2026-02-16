"""Prompt strategy templates for different subnet types"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PromptTemplateManager:
    """Manages subnet-specific prompt strategies and templates"""

    # Prompt templates for different strategies
    TEMPLATES = {
        'structured_reasoning': """You are an expert reasoning assistant. Analyze the following task and provide a structured response with clear reasoning steps.

Task: {task_content}

Please provide:
1. Understanding: What does this task ask?
2. Reasoning: What is your step-by-step reasoning?
3. Conclusion: What is your final answer?

Be clear, logical, and thorough.""",

        'concise_generation': """Provide a brief, direct response to the following task. Be concise and avoid unnecessary verbosity.

Task: {task_content}

Response:""",

        'calibrated_uncertainty': """Analyze the following task and provide a response that includes your confidence level.

Task: {task_content}

Please:
1. Provide your best answer/analysis
2. Rate your confidence (0-100%)
3. Note any uncertainties or limitations

Be honest about what you don't know.""",
    }

    # Strategy configurations
    STRATEGIES = {
        'structured_reasoning': {
            'description': 'Use chain-of-thought and explicit reasoning steps',
            'best_for': ['evaluation', 'ranking', 'complex_generation'],
            'token_multiplier': 1.2,
        },
        'concise_generation': {
            'description': 'Minimal verbosity, direct answers',
            'best_for': ['fast_generation'],
            'token_multiplier': 0.8,
        },
        'calibrated_uncertainty': {
            'description': 'Express confidence levels and uncertainty',
            'best_for': ['scoring', 'ranking', 'confidence_calibration'],
            'token_multiplier': 1.0,
        },
    }

    def __init__(self):
        self.custom_templates = {}
        logger.debug("PromptTemplateManager initialized")

    def get_template(self, strategy: str) -> Optional[str]:
        """Get prompt template for a strategy"""
        # Check custom templates first
        if strategy in self.custom_templates:
            return self.custom_templates[strategy]

        # Fall back to built-in templates
        if strategy in self.TEMPLATES:
            return self.TEMPLATES[strategy]

        logger.warning(f"Unknown prompt strategy: {strategy}")
        return self.TEMPLATES.get('structured_reasoning')  # Default fallback

    def get_strategy_info(self, strategy: str) -> Optional[Dict]:
        """Get configuration for a strategy"""
        return self.STRATEGIES.get(strategy)

    def apply_template(self, strategy: str, task_content: str) -> str:
        """Apply a strategy template to task content"""
        template = self.get_template(strategy)
        if not template:
            logger.error(f"No template found for strategy: {strategy}")
            return task_content

        try:
            return template.format(task_content=task_content)
        except KeyError as e:
            logger.error(f"Failed to apply template: {e}")
            return task_content

    def get_token_multiplier(self, strategy: str) -> float:
        """Get token budget multiplier for a strategy"""
        strategy_info = self.get_strategy_info(strategy)
        if strategy_info:
            return strategy_info.get('token_multiplier', 1.0)
        return 1.0

    def set_custom_template(self, strategy: str, template: str) -> None:
        """Register a custom template for a strategy"""
        self.custom_templates[strategy] = template
        logger.info(f"Registered custom template for strategy: {strategy}")

    def list_available_strategies(self) -> list:
        """List all available strategies"""
        strategies = list(self.TEMPLATES.keys()) + list(self.custom_templates.keys())
        return list(set(strategies))  # Remove duplicates

    def get_best_strategy_for_task_type(self, task_type: str) -> str:
        """Recommend best strategy for a task type"""
        task_type = task_type.lower()

        # Match task type to best strategy
        if task_type in ['evaluation', 'ranking', 'complex_generation']:
            return 'structured_reasoning'
        elif task_type in ['fast_generation', 'quick_response']:
            return 'concise_generation'
        elif task_type in ['scoring', 'confidence_calibration']:
            return 'calibrated_uncertainty'

        # Default to structured reasoning
        return 'structured_reasoning'
