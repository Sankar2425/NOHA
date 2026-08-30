from __future__ import annotations

# ----------------------------
# Brain
# ----------------------------

from runtime.brain.brain import Brain
from runtime.brain.context import BrainContext
from runtime.ai.ollama_client import OllamaClient
from runtime.brain.executor import Executor
from runtime.brain.intent_classifier import IntentClassifier
from runtime.brain.planner import Planner
from runtime.brain.reflection import Reflection
from runtime.brain.state import BrainState

# ----------------------------
# Runtime
# ----------------------------

from runtime.core.runtime_engine import RuntimeEngine

from runtime.tools.tool_registry import ToolRegistry


class RuntimeBuilder:
    """
    Builds the complete NOHA runtime.

    This is the application's Composition Root.
    """

    def build(self) -> RuntimeEngine:

        # ----------------------------------
        # Context & State
        # ----------------------------------

        context = BrainContext()
        state = BrainState()

        # ----------------------------------
        # Tool Registry
        # ----------------------------------

        tool_registry = ToolRegistry()

        # ----------------------------------
        # Brain Components
        # ----------------------------------

        classifier = IntentClassifier(OllamaClient())

        planner = Planner()

        executor = Executor(tool_registry)

        reflection = Reflection()

        # ----------------------------------
        # Brain
        # ----------------------------------

        brain = Brain(
            context=context,
            state=state,
            classifier=classifier,
            planner=planner,
            executor=executor,
            reflection=reflection,
        )

        # ----------------------------------
        # Runtime Engine
        # ----------------------------------

        runtime = RuntimeEngine(brain)

        return runtime
