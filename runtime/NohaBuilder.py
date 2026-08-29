from __future__ import annotations

# ----------------------------
# Brain
# ----------------------------

from runtime.brain.brain import Brain
from runtime.brain.context import BrainContext
from runtime.brain.executor import Executor
from runtime.brain.intent_classifier import IntentClassifier
from runtime.brain.planner import Planner
from runtime.brain.reflection import Reflection
from runtime.brain.state import BrainState

# ----------------------------
# Runtime
# ----------------------------

from runtime.core.runtime_engine import RuntimeEngine

# ----------------------------
# Registries
# ----------------------------

from runtime.skills.registry import SkillRegistry
from runtime.tools.tool_registry import ToolRegistry

# ----------------------------
# Skills
# ----------------------------

from runtime.skills.browser import BrowserSkill
from runtime.skills.coding import CodingSkill
from runtime.skills.filesystem import FilesystemSkill
from runtime.skills.memory import MemorySkill
from runtime.skills.terminal import TerminalSkill
from runtime.skills.application import ApplicationSkill

# ----------------------------
# Tools
# ----------------------------

from runtime.tools.browser_tool import BrowserTool
from runtime.tools.code_tool import CodeTool
from runtime.tools.file_tool import FileTool
from runtime.tools.memory_tool import MemoryTool
from runtime.tools.application_tool import ApplicationTool
from runtime.tools.run_code_tool import RunCodeTool
from runtime.tools.system_info_tool import SystemInfoTool
from runtime.tools.terminal_tool import TerminalTool


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

        tool_registry.register(FileTool())
        tool_registry.register(CodeTool())
        tool_registry.register(RunCodeTool())
        tool_registry.register(TerminalTool())
        tool_registry.register(BrowserTool())
        tool_registry.register(MemoryTool())
        tool_registry.register(SystemInfoTool())
        tool_registry.register(ApplicationTool())
         

        # ----------------------------------
        # Skill Registry
        # ----------------------------------

        skill_registry = SkillRegistry()

        skill_registry.register(
            FilesystemSkill(tool_registry)
        )

        skill_registry.register(
            CodingSkill(tool_registry)
        )

        skill_registry.register(
            TerminalSkill(tool_registry)
        )

        skill_registry.register(
            BrowserSkill(tool_registry)
        )

        skill_registry.register(
            MemorySkill(tool_registry)
        )

        skill_registry.register(
            ApplicationSkill(tool_registry)
        )

        # ----------------------------------
        # Brain Components
        # ----------------------------------

        classifier = IntentClassifier()

        planner = Planner()

        executor = Executor(skill_registry)

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