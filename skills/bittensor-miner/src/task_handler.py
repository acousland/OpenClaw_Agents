#!/usr/bin/env python3
"""
Task Handler
Bridges Bittensor tasks to LLM inference and response formatting.
Phase 1: Stub that logs tasks and returns echo responses.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from utils.prompt_templates import PromptTemplateManager
from utils.token_budget import TokenBudgetManager
from llm_router import LLMRouter

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "miner.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class TaskHandler:
    """
    Handles incoming Bittensor tasks.
    Routes to LLM, formats responses, logs results.
    """

    def __init__(self, config_path: str = "config/miner-config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.task_history_file = Path("state/task-history.jsonl")

        # Initialize components
        self.llm_router = LLMRouter()
        self.prompt_manager = PromptTemplateManager()
        self.budget_manager = TokenBudgetManager()

        logger.info("TaskHandler initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            logger.error(f"Config not found: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid config JSON: {e}")
            return {}

    def classify_task(self, task_content: str) -> Dict[str, Any]:
        """
        Classify an incoming task.
        Phase 1: Basic classification.

        Args:
            task_content: The task text/content

        Returns:
            Dict with task_type, reasoning_depth, time_sensitivity
        """
        classification = {
            'task_type': 'generation',  # generation, evaluation, ranking
            'reasoning_depth': 'medium',  # simple, medium, complex
            'time_sensitivity': 'normal',  # urgent, normal, flexible
            'confidence': 0.7,
        }
        return classification

    def should_respond(self, task: Dict[str, Any]) -> bool:
        """
        Decide whether to respond to a task.
        Phase 1: Always respond to test.

        Args:
            task: Task data including classification

        Returns:
            True if should respond, False if should skip
        """
        # Phase 1: Accept all tasks for testing
        return True

    def execute_inference(self, task: Dict[str, Any],
                          llm_config: Optional[Dict] = None) -> Optional[str]:
        """
        Execute LLM inference for a task.
        Phase 1: Return echo response.

        Args:
            task: Task data
            llm_config: LLM configuration (optional)

        Returns:
            Response text, or None if failed
        """
        try:
            logger.debug(f"Executing inference for task: {task.get('id', 'unknown')}")

            # Phase 1: Echo response (test mode)
            response = f"Echo response to: {task.get('content', '')[:100]}"

            logger.debug(f"Inference complete: {response[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return None

    def format_response(self, task: Dict[str, Any], response: str) -> str:
        """
        Format response per subnet requirements.
        Phase 1: Minimal formatting.

        Args:
            task: Task data
            response: Raw response text

        Returns:
            Formatted response
        """
        # Phase 1: Minimal formatting
        return response

    def process_task(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a complete task through the pipeline.
        Phase 1: Classify, decide, execute, format.

        Args:
            task: Task data from Bittensor

        Returns:
            Result dict with response and metadata, or None if failed
        """
        try:
            task_id = task.get('id', 'unknown')
            logger.info(f"Processing task {task_id}")

            # 1. Classify the task
            classification = self.classify_task(task.get('content', ''))
            task['classification'] = classification

            # 2. Decide whether to respond
            if not self.should_respond(task):
                logger.info(f"Skipping task {task_id}")
                return None

            # 3. Route to LLM
            llm_config = self.llm_router.select_llm(
                task_type=classification['task_type'],
                reasoning_depth=classification['reasoning_depth']
            )
            logger.debug(f"Selected LLM: {llm_config.get('model', 'default')}")

            # 4. Execute inference
            response = self.execute_inference(task, llm_config)
            if not response:
                logger.warning(f"Inference failed for task {task_id}")
                return None

            # 5. Format response
            formatted = self.format_response(task, response)

            # 6. Log result
            result = {
                'task_id': task_id,
                'response': formatted,
                'llm': llm_config.get('model', 'unknown'),
                'classification': classification,
                'status': 'success'
            }

            self._log_task_result(result)
            logger.info(f"✅ Task {task_id} processed successfully")

            return result

        except Exception as e:
            logger.error(f"Task processing failed: {e}", exc_info=True)
            return None

    def _log_task_result(self, result: Dict[str, Any]) -> None:
        """
        Log task result to history file.

        Args:
            result: Task result dict
        """
        try:
            self.task_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.task_history_file, 'a') as f:
                f.write(json.dumps(result) + '\n')
        except Exception as e:
            logger.error(f"Failed to log task result: {e}")

    def get_task_history(self, limit: int = 100) -> list:
        """Get recent task history"""
        try:
            if not self.task_history_file.exists():
                return []

            history = []
            with open(self.task_history_file, 'r') as f:
                for line in f:
                    try:
                        history.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

            return history[-limit:]  # Return last N tasks

        except Exception as e:
            logger.error(f"Failed to get task history: {e}")
            return []


def main():
    """Test task handler"""
    handler = TaskHandler()

    # Test task
    test_task = {
        'id': 'test_001',
        'content': 'What is 2+2?',
    }

    result = handler.process_task(test_task)
    if result:
        print(f"✅ Test successful: {result['response']}")
    else:
        print("❌ Test failed")


if __name__ == "__main__":
    main()
