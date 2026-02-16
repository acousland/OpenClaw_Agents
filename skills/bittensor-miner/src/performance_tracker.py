#!/usr/bin/env python3
"""
Performance Tracker
Analyzes results and adapts strategy based on validator feedback.
Phase 1: Data collection and basic metrics.
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from collections import defaultdict

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "performance.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class PerformanceTracker:
    """
    Tracks task performance and adapts mining strategy.
    Phase 1: Collects metrics, identifies trends.
    """

    def __init__(self, history_file: str = "state/task-history.jsonl",
                 metrics_file: str = "state/performance-metrics.json"):
        self.history_file = Path(history_file)
        self.metrics_file = Path(metrics_file)
        logger.debug("PerformanceTracker initialized")

    def record_task_result(self, task_id: str, validator_score: float,
                          tokens_spent: int, llm_used: str,
                          prompt_strategy: str, subnet_id: int = 1) -> None:
        """
        Record result of a completed task.

        Args:
            task_id: Unique task identifier
            validator_score: Validator score (0-1)
            tokens_spent: Tokens consumed
            llm_used: Which LLM was used
            prompt_strategy: Which strategy was used
            subnet_id: Target subnet
        """
        try:
            result = {
                'timestamp': datetime.utcnow().isoformat(),
                'task_id': task_id,
                'validator_score': validator_score,
                'tokens_spent': tokens_spent,
                'llm_used': llm_used,
                'prompt_strategy': prompt_strategy,
                'subnet_id': subnet_id,
            }

            # Append to history
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, 'a') as f:
                f.write(json.dumps(result) + '\n')

            logger.debug(f"Recorded task {task_id}: score={validator_score}")

        except Exception as e:
            logger.error(f"Failed to record task result: {e}")

    def analyze_performance(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze performance over a time window.
        Phase 1: Basic statistics.

        Args:
            days: Number of days to analyze

        Returns:
            Dict with performance metrics
        """
        try:
            history = self._load_history()

            # Filter to time window
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            filtered = [
                task for task in history
                if datetime.fromisoformat(task.get('timestamp', ''))
                > cutoff_time
            ]

            if not filtered:
                logger.warning(f"No tasks in {days}-day window")
                return self._empty_metrics()

            # Calculate metrics
            metrics = {
                'period_days': days,
                'tasks_completed': len(filtered),
                'average_score': sum(t.get('validator_score', 0) for t in filtered) / len(filtered),
                'success_rate': sum(1 for t in filtered if t.get('validator_score', 0) > 0.5) / len(filtered),
                'total_tokens_spent': sum(t.get('tokens_spent', 0) for t in filtered),
                'by_llm': self._analyze_by_llm(filtered),
                'by_strategy': self._analyze_by_strategy(filtered),
            }

            return metrics

        except Exception as e:
            logger.error(f"Failed to analyze performance: {e}")
            return self._empty_metrics()

    def _analyze_by_llm(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Analyze performance by LLM"""
        by_llm = defaultdict(list)
        for task in tasks:
            llm = task.get('llm_used', 'unknown')
            by_llm[llm].append(task.get('validator_score', 0))

        result = {}
        for llm, scores in by_llm.items():
            result[llm] = {
                'tasks': len(scores),
                'avg_score': sum(scores) / len(scores),
                'success_rate': sum(1 for s in scores if s > 0.5) / len(scores),
            }
        return result

    def _analyze_by_strategy(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Analyze performance by prompt strategy"""
        by_strategy = defaultdict(list)
        for task in tasks:
            strategy = task.get('prompt_strategy', 'unknown')
            by_strategy[strategy].append(task.get('validator_score', 0))

        result = {}
        for strategy, scores in by_strategy.items():
            result[strategy] = {
                'tasks': len(scores),
                'avg_score': sum(scores) / len(scores),
                'success_rate': sum(1 for s in scores if s > 0.5) / len(scores),
            }
        return result

    def _load_history(self) -> List[Dict[str, Any]]:
        """Load task history from file"""
        if not self.history_file.exists():
            return []

        history = []
        try:
            with open(self.history_file, 'r') as f:
                for line in f:
                    try:
                        history.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Failed to load history: {e}")

        return history

    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics dict"""
        return {
            'period_days': 0,
            'tasks_completed': 0,
            'average_score': 0.0,
            'success_rate': 0.0,
            'total_tokens_spent': 0,
            'by_llm': {},
            'by_strategy': {},
        }

    def save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save metrics to file"""
        try:
            metrics['last_updated'] = datetime.utcnow().isoformat()
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            logger.debug("Metrics saved")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

    def get_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on performance.
        Phase 1: Simple heuristics.

        Args:
            metrics: Performance metrics dict

        Returns:
            List of recommendation strings
        """
        recommendations = []

        avg_score = metrics.get('average_score', 0)
        if avg_score < 0.6:
            recommendations.append("Average score is low. Consider adjusting prompt strategies.")

        success_rate = metrics.get('success_rate', 0)
        if success_rate < 0.5:
            recommendations.append("Task success rate is poor. Review task selection logic.")

        # Find best LLM
        by_llm = metrics.get('by_llm', {})
        if by_llm:
            best_llm = max(by_llm.items(), key=lambda x: x[1].get('avg_score', 0))
            recommendations.append(f"Best performing LLM: {best_llm[0]}")

        # Find best strategy
        by_strategy = metrics.get('by_strategy', {})
        if by_strategy:
            best_strategy = max(by_strategy.items(), key=lambda x: x[1].get('avg_score', 0))
            recommendations.append(f"Best performing strategy: {best_strategy[0]}")

        return recommendations

    def generate_report(self, days: int = 7) -> str:
        """Generate a human-readable performance report"""
        metrics = self.analyze_performance(days=days)
        recommendations = self.get_recommendations(metrics)

        report_lines = [
            f"\n📊 Performance Report ({days}-day window)",
            "=" * 50,
            f"Tasks completed: {metrics['tasks_completed']}",
            f"Average score: {metrics['average_score']:.2f}",
            f"Success rate: {metrics['success_rate']:.1%}",
            f"Tokens spent: {metrics['total_tokens_spent']}",
        ]

        if recommendations:
            report_lines.append("\n💡 Recommendations:")
            for rec in recommendations:
                report_lines.append(f"  - {rec}")

        return '\n'.join(report_lines)


def main():
    """Test performance tracker"""
    tracker = PerformanceTracker()

    # Record some test results
    for i in range(5):
        tracker.record_task_result(
            task_id=f"test_{i}",
            validator_score=0.7 + (i * 0.02),
            tokens_spent=500 + (i * 100),
            llm_used="openai-gpt4",
            prompt_strategy="structured_reasoning",
            subnet_id=1
        )

    # Analyze
    metrics = tracker.analyze_performance(days=1)
    print(tracker.generate_report(days=1))

    # Save
    tracker.save_metrics(metrics)


if __name__ == "__main__":
    main()
