from fastmcp import FastMCP
import sys
import logging
import os

# Import modular components
from src.client import MuseScoreClient
from src.context.service import ContextService
from src.tools.arrangement import setup_arrangement_tools
from src.tools import (
    setup_connection_tools,
    setup_navigation_tools,
    setup_notes_measures_tools,
    setup_staff_instruments_tools,
    setup_time_tempo_tools,
    setup_sequence_tools,
    setup_viewer_tools,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("MuseScoreMCP")

# Create the MCP app and client
mcp = FastMCP("MuseScore Evolution Assistant", instructions=(
    "Control the open MuseScore 3 Evolution score through its local plugin. "
    "Ping first; use get_capabilities and get_score_data before editing. "
    "Measures are 1-based, staves and voices 0-based. "
    "Read back after edits. A failed write may already have applied: inspect before retrying. "
    "Sequences stop on failure but do not roll back completed actions. "
    "set_staff_mute is a legacy visibility operation unsupported on MuseScore 3, not audio mute; "
    "set_instrument_sound opens a manual dialog. Use MuseScore for final layout verification."
))
client = MuseScoreClient(host=os.environ.get("MCP_MUSESCORE_HOST", "127.0.0.1"),
                        port=int(os.environ.get("MCP_MUSESCORE_PORT", "8765")))

# One context service is shared by the tools and local callers.
context_service = ContextService(client)
setup_arrangement_tools(mcp, context_service)

# Setup all tool categories
setup_connection_tools(mcp, client, context_service)
setup_navigation_tools(mcp, client)
setup_notes_measures_tools(mcp, client)
setup_staff_instruments_tools(mcp, client)
setup_time_tempo_tools(mcp, client)
setup_sequence_tools(mcp, client)
setup_viewer_tools(mcp, client)

# Main entry point
if __name__ == "__main__":
    mcp.run()
