from __future__ import annotations

import webbrowser

from runtime.tools.base_tool import BaseTool


class OpenWebsiteTool(BaseTool):
    """
    Opens a website in the user's default browser.
    """

    name = "open_website_tool"
    description = "Opens websites in the default browser."

    async def execute(
        self,
        payload: dict,
    ) -> dict:

        url = payload.get("url")

        if not url:
            return {
                "status": "error",
                "message": "No URL provided.",
            }

        try:

            if not (
                url.startswith("http://")
                or url.startswith("https://")
            ):
                url = f"https://{url}"

            opened = webbrowser.open(url)

            return {
                "status": "success",
                "url": url,
                "opened": opened,
            }

        except Exception as exc:

            return {
                "status": "error",
                "message": str(exc),
            }