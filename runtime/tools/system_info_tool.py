from __future__ import annotations

import os
import platform
import socket

import psutil 

from runtime.tools.base_tool import BaseTool


class SystemInfoTool(BaseTool):
    """
    Retrieves system information.
    """

    name = "system"
    description = "Returns information about the host system."

    async def execute(
        self,
        payload: dict,
    ) -> dict:

        action = payload.get("action", "summary")

        try:

            if action == "summary":
                return self._summary()

            elif action == "cpu":
                return self._cpu()

            elif action == "memory":
                return self._memory()

            elif action == "disk":
                return self._disk()

            elif action == "network":
                return self._network()

            elif action == "os":
                return self._os()

            return {
                "status": "error",
                "message": f"Unknown action '{action}'.",
            }

        except Exception as exc:

            return {
                "status": "error",
                "message": str(exc),
            }

    # -----------------------------------------------------

    def _summary(self):

        return {
            "status": "success",
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "release": platform.release(),
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage(os.getcwd()).percent,
        }

    # -----------------------------------------------------

    def _cpu(self):

        return {
            "status": "success",
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "usage_percent": psutil.cpu_percent(interval=1),
            "frequency": psutil.cpu_freq().current
            if psutil.cpu_freq()
            else None,
        }

    # -----------------------------------------------------

    def _memory(self):

        memory = psutil.virtual_memory()

        return {
            "status": "success",
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
        }

    # -----------------------------------------------------

    def _disk(self):

        disk = psutil.disk_usage("/")

        return {
            "status": "success",
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }

    # -----------------------------------------------------

    def _network(self):

        return {
            "status": "success",
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
        }

    # -----------------------------------------------------

    def _os(self):

        return {
            "status": "success",
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }