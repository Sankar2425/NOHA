from __future__ import annotations

import shutil
from pathlib import Path

from runtime.brain.enums import TaskAction
from runtime.tools.base_tool import BaseTool


class FileTool(BaseTool):
    """
    Handles filesystem operations inside NOHA's workspace.

    All filesystem operations are restricted to the NOHA workspace.
    Paths attempting to escape the workspace are rejected.
    """

    name = "filesystem"
    description = "Performs file and folder operations."

    WORKSPACE = Path("workspace")

    def __init__(self) -> None:
        """Initialize the filesystem tool."""

        self.WORKSPACE.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    async def execute(self, payload: dict) -> dict:
        """
        Execute a filesystem action.

        Expected payload format:

        {
            "action": "create_file",
            "path": "test/app.py"
        }

        Additional parameters are used depending on the action.
        """

        if not isinstance(payload, dict):
            return {
                "status": "error",
                "message": "Payload must be a dictionary.",
            }

        action = payload.get("action")

        if not action:
            return {
                "status": "error",
                "message": "No action provided.",
            }

        try:

            # --------------------------------------------------
            # CREATE FOLDER
            # --------------------------------------------------

            if action == TaskAction.CREATE_FOLDER.value:

                return self._create_folder(
                    payload.get("path")
                )

            # --------------------------------------------------
            # CREATE FILE
            # --------------------------------------------------

            elif action == TaskAction.CREATE_FILE.value:

                return self._create_file(
                    payload.get("path")
                )

            # --------------------------------------------------
            # WRITE FILE
            # --------------------------------------------------

            elif action == TaskAction.WRITE_FILE.value:

                return self._write_file(
                    payload.get("path"),
                    payload.get("content", ""),
                )

            # --------------------------------------------------
            # READ FILE
            # --------------------------------------------------

            elif action == TaskAction.READ_FILE.value:

                return self._read_file(
                    payload.get("path")
                )

            # --------------------------------------------------
            # DELETE FILE
            # --------------------------------------------------

            elif action == TaskAction.DELETE_FILE.value:

                return self._delete_file(
                    payload.get("path")
                )

            # --------------------------------------------------
            # RENAME FILE
            # --------------------------------------------------

            elif action == TaskAction.RENAME_FILE.value:

                return self._rename_file(
                    payload.get("old_path"),
                    payload.get("new_path"),
                )

            # --------------------------------------------------
            # COPY FILE
            # --------------------------------------------------

            elif action == TaskAction.COPY_FILE.value:

                return self._copy_file(
                    payload.get("source"),
                    payload.get("destination"),
                )

            # --------------------------------------------------
            # MOVE FILE
            # --------------------------------------------------

            elif action == TaskAction.MOVE_FILE.value:

                return self._move_file(
                    payload.get("source"),
                    payload.get("destination"),
                )

            # --------------------------------------------------
            # LIST FILES
            # --------------------------------------------------

            elif action == TaskAction.LIST_FILES.value:

                return self._list_files()

            # --------------------------------------------------
            # UNKNOWN ACTION
            # --------------------------------------------------

            return {
                "status": "error",
                "message": f"Unsupported action '{action}'.",
            }

        except Exception as exc:

            return {
                "status": "error",
                "message": str(exc),
            }

    # ==========================================================
    # PATH SECURITY
    # ==========================================================

    def _resolve(self, path: str) -> Path:
        """
        Resolve a path safely inside the NOHA workspace.

        Prevents:
            ../
            ../../
            absolute paths
            symlink escapes

        Example:

            "projects/app.py"

        becomes:

            workspace/projects/app.py
        """

        if not isinstance(path, str):
            raise TypeError("Path must be a string.")

        path = path.strip()

        if not path:
            raise ValueError("Path cannot be empty.")

        # Resolve the workspace itself.
        workspace = self.WORKSPACE.resolve()

        # Resolve the requested target.
        target = (workspace / path).resolve()

        # Make sure the final resolved path is still
        # inside the workspace.
        try:

            target.relative_to(workspace)

        except ValueError as exc:

            raise PermissionError(
                f"Path escapes NOHA workspace: {path}"
            ) from exc

        return target

    # ==========================================================
    # CREATE FOLDER
    # ==========================================================

    def _create_folder(self, path: str) -> dict:
        """Create a folder inside the workspace."""

        folder = self._resolve(path)

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return {
            "status": "success",
            "message": f"Folder created: {path}",
            "path": str(folder),
        }

    # ==========================================================
    # CREATE FILE
    # ==========================================================

    def _create_file(self, path: str) -> dict:
        """Create an empty file inside the workspace."""

        file = self._resolve(path)

        # Create parent directories automatically.
        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file.touch(
            exist_ok=True,
        )

        return {
            "status": "success",
            "message": f"File created: {path}",
            "path": str(file),
        }

    # ==========================================================
    # WRITE FILE
    # ==========================================================

    def _write_file(
        self,
        path: str,
        content: str,
    ) -> dict:
        """Write text content to a file."""

        if not isinstance(content, str):
            raise TypeError(
                "File content must be a string."
            )

        file = self._resolve(path)

        file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file.write_text(
            content,
            encoding="utf-8",
        )

        return {
            "status": "success",
            "message": f"Wrote file: {path}",
            "path": str(file),
            "bytes": file.stat().st_size,
        }

    # ==========================================================
    # READ FILE
    # ==========================================================

    def _read_file(self, path: str) -> dict:
        """Read a text file."""

        file = self._resolve(path)

        if not file.exists():
            raise FileNotFoundError(
                f"File does not exist: {path}"
            )

        if not file.is_file():
            raise IsADirectoryError(
                f"Path is not a file: {path}"
            )

        content = file.read_text(
            encoding="utf-8",
        )

        return {
            "status": "success",
            "path": str(file),
            "content": content,
        }

    # ==========================================================
    # DELETE FILE
    # ==========================================================

    def _delete_file(self, path: str) -> dict:
        """Delete a file inside the workspace."""

        file = self._resolve(path)

        if not file.exists():
            raise FileNotFoundError(
                f"File does not exist: {path}"
            )

        if not file.is_file():
            raise IsADirectoryError(
                f"Path is not a file: {path}"
            )

        file.unlink()

        return {
            "status": "success",
            "message": f"Deleted: {path}",
            "path": str(file),
        }

    # ==========================================================
    # RENAME FILE
    # ==========================================================

    def _rename_file(
        self,
        old_path: str,
        new_path: str,
    ) -> dict:
        """Rename a file inside the workspace."""

        source = self._resolve(old_path)
        destination = self._resolve(new_path)

        if not source.exists():
            raise FileNotFoundError(
                f"Source does not exist: {old_path}"
            )

        if not source.is_file():
            raise IsADirectoryError(
                f"Source is not a file: {old_path}"
            )

        if destination.exists():
            raise FileExistsError(
                f"Destination already exists: {new_path}"
            )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        source.rename(destination)

        return {
            "status": "success",
            "message": (
                f"Renamed '{old_path}' → '{new_path}'"
            ),
            "old_path": str(source),
            "new_path": str(destination),
        }

    # ==========================================================
    # COPY FILE
    # ==========================================================

    def _copy_file(
        self,
        source: str,
        destination: str,
    ) -> dict:
        """Copy a file inside the workspace."""

        src = self._resolve(source)
        dst = self._resolve(destination)

        if not src.exists():
            raise FileNotFoundError(
                f"Source does not exist: {source}"
            )

        if not src.is_file():
            raise IsADirectoryError(
                f"Source is not a file: {source}"
            )

        if dst.exists():
            raise FileExistsError(
                f"Destination already exists: {destination}"
            )

        dst.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.copy2(
            src,
            dst,
        )

        return {
            "status": "success",
            "message": (
                f"Copied '{source}' → '{destination}'"
            ),
            "source": str(src),
            "destination": str(dst),
        }

    # ==========================================================
    # MOVE FILE
    # ==========================================================

    def _move_file(
        self,
        source: str,
        destination: str,
    ) -> dict:
        """Move a file inside the workspace."""

        src = self._resolve(source)
        dst = self._resolve(destination)

        if not src.exists():
            raise FileNotFoundError(
                f"Source does not exist: {source}"
            )

        if not src.is_file():
            raise IsADirectoryError(
                f"Source is not a file: {source}"
            )

        if dst.exists():
            raise FileExistsError(
                f"Destination already exists: {destination}"
            )

        dst.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        shutil.move(
            src,
            dst,
        )

        return {
            "status": "success",
            "message": (
                f"Moved '{source}' → '{destination}'"
            ),
            "source": str(src),
            "destination": str(dst),
        }

    # ==========================================================
    # LIST FILES
    # ==========================================================

    def _list_files(self) -> dict:
        """List all files and folders inside the workspace."""

        files = []

        for item in self.WORKSPACE.rglob("*"):

            files.append(
                str(
                    item.relative_to(
                        self.WORKSPACE
                    )
                )
            )

        return {
            "status": "success",
            "files": sorted(files),
        }