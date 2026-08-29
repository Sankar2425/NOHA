from __future__ import annotations

from runtime.brain.enums import ReflectionStatus
from runtime.brain.models import (
    ExecutionResult,
    ReflectionResult,
)


class Reflection:
    """
    Evaluates the outcome of a completed execution.

    Reflection never executes tasks or modifies plans.
    It only analyzes the execution result and recommends
    the next course of action.
    """

    async def reflect(
        self,
        result: ExecutionResult,
    ) -> ReflectionResult:
        """
        Analyze an execution result.
        """

        if result.success:
            return ReflectionResult(
                status=ReflectionStatus.SUCCESS,
                should_retry=False,
                message=result.message,
                recommendations=[],
            )

        recommendations = []

        if result.failed_tasks > 0:
            recommendations.append(
                "Inspect the failed task(s)."
            )

        recommendations.append(
            "Review tool output and logs."
        )

        recommendations.append(
            "Retry execution if the failure was temporary."
        )

        return ReflectionResult(
            status=ReflectionStatus.RETRY,
            should_retry=True,
            message=result.message,
            recommendations=recommendations,
        )