"""WebSocket client for communicating with MuseScore."""

import websockets
import json
import logging
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger("MuseScoreMCP.Client")


class MuseScoreClient:
    """Client to communicate with MuseScore WebSocket API."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8765, timeout: float = 15):
        self.uri = f"ws://{host}:{port}"
        self.websocket = None
        self.timeout = timeout
        self._lock = None
        self._loop = None
        self.connection_resolver = None
        self.connection_error = ""

    def _command_lock(self):
        # Tests/embedders may reuse a client across sequential event loops.
        loop = asyncio.get_running_loop()
        if self._loop is not loop:
            self._lock = asyncio.Lock()
            self._loop = loop
        return self._lock
    
    async def connect(self):
        async with self._command_lock():
            await self._reset_socket()
            return await self._connect()

    async def _connect(self):
        """Connect to the MuseScore WebSocket API."""
        try:
            if self.connection_resolver is not None:
                host, port = self.connection_resolver()
                self.uri = f"ws://{host}:{port}"
            self.websocket = await websockets.connect(self.uri, open_timeout=self.timeout, close_timeout=2, max_size=16 * 1024 * 1024)
            self.connection_error = ""
            logger.info(f"Connected to MuseScore API at {self.uri}")
            return True
        except Exception as e:
            self.connection_error = str(e) if self.connection_resolver is not None else ""
            logger.error(f"Failed to connect to MuseScore API: {str(e)}")
            return False
    
    async def _reset_socket(self):
        """Drop the current socket so the next call reconnects from scratch.

        MuseScore restarting (or the plugin reloading) leaves us holding a dead
        socket whose send/recv raises. Nulling it here lets send_command pick up
        a fresh connection without the whole MCP server needing a restart.
        """
        if self.websocket is not None:
            try:
                await self.websocket.close()
            except Exception:
                pass
            self.websocket = None

    async def send_command(self, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Serialize request/response pairs; never replay an ambiguous write."""
        async with self._command_lock():
            return await self._send_command(action, params)

    async def _send_command(self, action, params):
        if params is None:
            params = {}

        if self.connection_resolver is not None:
            try:
                host, port = self.connection_resolver()
                uri = f"ws://{host}:{port}"
                if uri != self.uri:
                    await self._reset_socket()
                    self.uri = uri
            except Exception as error:
                await self._reset_socket()
                return {"error": str(error)}

        command = {"action": action, "params": params}
        payload = json.dumps(command)

        last_error: Optional[str] = None
        read_only = action in {"ping", "getCapabilities", "getScoreIdentity", "arrangementImage", "getScore", "getCursorInfo", "arrangementState", "arrangementRange", "arrangementPlaybackPrepare", "arrangementPlaybackPage", "arrangementSuggestions", "arrangementOperationStatus"}
        attempts = 2 if read_only else 1
        for attempt in range(attempts):
            if not self.websocket:
                if not await self._connect():
                    return {"error": self.connection_error or "Not connected to MuseScore"}

            try:
                logger.info("Sending %s (%d bytes)", action, len(payload.encode("utf8")))
                await self.websocket.send(payload)
                response = await asyncio.wait_for(self.websocket.recv(), self.timeout)
                logger.info("Received %s response (%d bytes)", action, len(response.encode("utf8")))
                return json.loads(response)
            except asyncio.CancelledError:
                await self._reset_socket()
                raise
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Send failed (attempt {attempt + 1}/{attempts}), resetting socket: {last_error}"
                )
                await self._reset_socket()

        if not read_only:
            return {"error": "MuseScore write response was lost; the action may have applied. Read the score before retrying.",
                    "outcomeUnknown": True, "detail": last_error}
        return {"error": f"Not connected to MuseScore: {last_error}"}

    async def close(self):
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            logger.info("Disconnected from MuseScore API")
