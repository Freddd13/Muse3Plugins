import os
os.environ.setdefault("FASTMCP_CHECK_FOR_UPDATES", "off")
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
    "通过本机连接操作当前打开的 MuseScore 乐谱。先用get_score_identity确认当前窗口、谱面标题、总谱／分谱和未保存状态，再按需要读取当前选区。"
    "编配任务使用 read_arrangement_context 分批读取内存中的音符、声部、和弦与演奏数据；"
    "需要核对谱面时，用get_score_image按同一context_id读取MuseScore原图和音符位置。"
    "分析默认读取完整记谱；比较实际力度、起音和踏板时用purpose=performance，检查排版时用purpose=engraving。"
    "notatedPitch是谱面音高，concertPitch是实音，soundingPitch是播放音高；参考录音时间采用毫秒。"
    "继续已有任务时用refresh_arrangement_context保留原范围与要求，补充读取当前修改。"
    "保留任务范围，按需要补充材料和解释。给出少量局部写法，用编配建议面板比较、试听和采用。"
    "用户明确要求修改时，在指定范围完成编辑并读回核对；一次采用形成一次撤销。"
    "小节从 1 开始，谱表和声部从 0 开始。写入响应中断时，先查询操作结果或重新读谱，再决定后续操作。"
    "普通操作序列按顺序执行，返回每步结果；中途失败时先核对已经完成的步骤。"
))
client = MuseScoreClient(host=os.environ.get("MCP_MUSESCORE_HOST", "127.0.0.1"),
                        port=int(os.environ.get("MCP_MUSESCORE_PORT", "8765")))

# One context service is shared by the tools and local callers.
context_service = ContextService(client)
setup_arrangement_tools(mcp, context_service)

# Setup all tool categories
setup_connection_tools(mcp, client, context_service)
setup_navigation_tools(mcp, client, context_service)
setup_notes_measures_tools(mcp, client)
setup_staff_instruments_tools(mcp, client)
setup_time_tempo_tools(mcp, client)
setup_sequence_tools(mcp, client)
setup_viewer_tools(mcp, client, context_service)

# Main entry point
if __name__ == "__main__":
    mcp.run(show_banner=False)
