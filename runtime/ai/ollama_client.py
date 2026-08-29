from __future__ import annotations

import httpx

from runtime.config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_STREAM,
)


class OllamaClient:
    """
    Async client for communicating with the local Ollama server.

    Responsibilities
    ----------------
    - Connect to Ollama
    - Send prompts
    - Receive raw model responses
    - Handle HTTP and connection errors

    This class does NOT:
    - Parse NOHA JSON
    - Validate intents
    - Build IntentResult objects
    - Make execution decisions
    """

    def __init__(
        self,
        host: str = OLLAMA_HOST,
        model: str = OLLAMA_MODEL,
        timeout: int = OLLAMA_TIMEOUT,
    ) -> None:

        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    async def generate(self, prompt: str) -> str:
        """
        Send a prompt to Ollama and return the raw model response.
        """

        if not isinstance(prompt, str):
            raise TypeError(
                "Prompt must be a string."
            )

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "Prompt cannot be empty."
            )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": OLLAMA_STREAM,
        }

        data = await self._post(payload)

        # ------------------------------------------------------
        # Validate Ollama response
        # ------------------------------------------------------

        if "response" not in data:
            raise RuntimeError(
                "Ollama response does not contain a 'response' field."
            )

        response = data["response"]

        if not isinstance(response, str):
            raise TypeError(
                "Ollama response must be a string."
            )

        response = response.strip()

        if not response:
            raise ValueError(
                "Ollama returned an empty response."
            )

        return response

    # ==========================================================
    # INTERNAL HTTP REQUEST
    # ==========================================================

    async def _post(self, payload: dict) -> dict:
        """
        Send a POST request to the Ollama generate endpoint.
        """

        url = f"{self.host}/api/generate"

        try:

            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:

                response = await client.post(
                    url,
                    json=payload,
                )

            # --------------------------------------------------
            # HTTP Error
            # --------------------------------------------------

            if response.status_code >= 400:

                error_body = response.text.strip()

                raise RuntimeError(
                    "Ollama request failed.\n"
                    f"Status: {response.status_code}\n"
                    f"URL: {url}\n"
                    f"Response: {error_body}"
                )

            # --------------------------------------------------
            # Parse JSON
            # --------------------------------------------------

            try:

                data = response.json()

            except ValueError as exc:

                raise RuntimeError(
                    "Ollama returned an invalid JSON response."
                ) from exc

            if not isinstance(data, dict):

                raise RuntimeError(
                    "Ollama returned an unexpected response format."
                )

            return data

        # ------------------------------------------------------
        # Connection Error
        # ------------------------------------------------------

        except httpx.ConnectError as exc:

            raise ConnectionError(
                "Unable to connect to Ollama.\n"
                f"Host: {self.host}\n"
                "Make sure the Ollama server is running."
            ) from exc

        # ------------------------------------------------------
        # Timeout
        # ------------------------------------------------------

        except httpx.TimeoutException as exc:

            raise TimeoutError(
                "Ollama request timed out.\n"
                f"Timeout: {self.timeout} seconds"
            ) from exc

        # ------------------------------------------------------
        # Preserve our own RuntimeError
        # ------------------------------------------------------

        except RuntimeError:

            raise

        # ------------------------------------------------------
        # Unexpected Error
        # ------------------------------------------------------

        except Exception as exc:

            raise RuntimeError(
                f"Unexpected Ollama client error: {exc}"
            ) from exc