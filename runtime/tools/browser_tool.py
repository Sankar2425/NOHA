from __future__ import annotations

import webbrowser
from urllib.parse import quote_plus

from runtime.tools.base_tool import BaseTool


class BrowserTool(BaseTool):
    """
    Tool responsible for browser-related operations.
    """

    name = "browser"

    async def execute(
        self,
        payload: dict,
    ) -> dict:

        action = payload.get("action", "").lower()

        if action == "open_url":
            return self._open_url(payload)

        if action == "search_web":
            return self._search_web(payload)

        return {
            "status": "error",
            "message": f"Unsupported browser action: {action}",
        }

    def _open_url(
        self,
        payload: dict,
    ) -> dict:

        url = payload.get("url", "").strip()

        if not url:
            return {
                "status": "error",
                "message": "No URL provided.",
            }

        if not (
            url.startswith("http://")
            or url.startswith("https://")
        ):
            url = f"https://{url}"

        try:
            opened = webbrowser.open(url)

        except Exception as exc:
            return {
                "status": "error",
                "message": str(exc),
            }

        if not opened:
            return {
                "status": "error",
                "message": f"No browser could open {url}.",
                "url": url,
            }

        return {
            "status": "success",
            "message": f"Opened {url}",
            "url": url,
        }

    def _search_web(
        self,
        payload: dict,
    ) -> dict:

        query = payload.get("query", "").strip()

        if not query:
            return {
                "status": "error",
                "message": "Search query is empty.",
            }

        url = (
            "https://www.google.com/search?q="
            + quote_plus(query)
        )

        try:
            opened = webbrowser.open(url)

        except Exception as exc:
            return {
                "status": "error",
                "message": str(exc),
            }

        if not opened:
            return {
                "status": "error",
                "message": "No browser could open the search URL.",
                "url": url,
            }

        return {
            "status": "success",
            "message": f'Searching for "{query}"',
            "url": url,
        }
