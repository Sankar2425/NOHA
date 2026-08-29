from __future__ import annotations

from enum import Enum


# ==========================================================
# TASK
# ==========================================================

class TaskStatus(str, Enum):
    """Execution state of an individual task."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class TaskAction(str, Enum):
    """Specific action a task should perform."""

    # Filesystem
    CREATE_FOLDER = "create_folder"
    CREATE_FILE = "create_file"
    WRITE_FILE = "write_file"
    READ_FILE = "read_file"
    DELETE_FILE = "delete_file"
    RENAME_FILE = "rename_file"
    COPY_FILE = "copy_file"
    MOVE_FILE = "move_file"
    LIST_FILES = "list_files"

    # Coding
    GENERATE_CODE = "generate_code"
    MODIFY_CODE = "modify_code"
    ANALYZE_CODE = "analyze_code"
    RUN_CODE = "run_code"

    # Terminal
    RUN_COMMAND = "run_command"

    # Browser
    OPEN_URL = "open_url"
    SEARCH_WEB = "search_web"

    # Applications
    APPLICATION="application"

    # Memory
    SAVE_MEMORY = "save_memory"
    LOAD_MEMORY = "load_memory"
    DELETE_MEMORY = "delete_memory"
    LIST_MEMORY = "list_memory"

    # Vision
    ANALYZE_IMAGE = "analyze_image"

    # Voice
    SPEAK = "speak"
    LISTEN = "listen"

    UNKNOWN = "unknown"


# ==========================================================
# PLAN
# ==========================================================

class PlanStatus(str, Enum):
    """Execution state of an entire plan."""

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"
    CANCELLED = "cancelled"


# ==========================================================
# EXECUTION
# ==========================================================

class ExecutionStatus(str, Enum):
    """Runtime execution state."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    FAILED = "failed"


# ==========================================================
# REFLECTION
# ==========================================================

class ReflectionStatus(str, Enum):
    """Outcome of the reflection phase."""

    NOT_REQUIRED = "not_required"
    RETRY = "retry"
    REPAIR = "repair"
    ESCALATE = "escalate"
    SUCCESS = "success"


# ==========================================================
# INTENT
# ==========================================================

class IntentType(str, Enum):
    """High-level user intent."""

    CHAT = "chat"

    FILESYSTEM = "filesystem"
    CODING = "coding"
    TERMINAL = "terminal"
    MEMORY = "memory"

    BROWSER = "browser"
    APPLICATION = "application"

    AUTOMATION = "automation"

    VISION = "vision"
    VOICE = "voice"

    RESPOND = "respond"

    SYSTEM = "system"

    UNKNOWN = "unknown"


# ==========================================================
# SKILLS
# ==========================================================

class SkillType(str, Enum):
    """Available executable skills."""

    FILESYSTEM = "filesystem"

    CODING = "coding"

    TERMINAL = "terminal"

    MEMORY = "memory"

    BROWSER = "browser"

    APPLICATION = "application"

    VISION = "vision"

    VOICE = "voice"

    AUTOMATION = "automation"

    CHAT = "chat"