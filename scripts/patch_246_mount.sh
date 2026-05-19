#!/usr/bin/env bash
set -euo pipefail

APP_CONFIGS="/home/mkjang/onyx-worktrees/origin-main-deploy/backend/onyx/configs/app_configs.py"
COMPOSE_FILE="/home/mkjang/onyx-worktrees/origin-main-deploy/deployment/docker_compose/docker-compose.yml"

python3 - <<'PY'
from pathlib import Path
import re

app_configs = Path("/home/mkjang/onyx-worktrees/origin-main-deploy/backend/onyx/configs/app_configs.py")
text = app_configs.read_text(encoding="utf-8")
needle = """# Safety valve for explicit raw-output mode during debugging.\nMCP_SERVER_ALLOW_RAW_OUTPUT = (\n    os.environ.get(\"MCP_SERVER_ALLOW_RAW_OUTPUT\", \"false\").lower() == \"true\"\n)\n"""
insert = needle + """\nFILE_CONNECTOR_STRUCTURE_AWARE_CHUNKING = (\n    os.environ.get(\"FILE_CONNECTOR_STRUCTURE_AWARE_CHUNKING\", \"false\").lower()\n    == \"true\"\n)\n\nFILE_CONNECTOR_CONTEXTUAL_ENRICHMENT = (\n    os.environ.get(\"FILE_CONNECTOR_CONTEXTUAL_ENRICHMENT\", \"false\").lower()\n    == \"true\"\n)\n"""
if "FILE_CONNECTOR_STRUCTURE_AWARE_CHUNKING" not in text:
    if needle not in text:
        raise SystemExit("app_configs marker not found")
    text = text.replace(needle, insert, 1)
    app_configs.write_text(text, encoding="utf-8")

compose = Path("/home/mkjang/onyx-worktrees/origin-main-deploy/deployment/docker_compose/docker-compose.yml")
text = compose.read_text(encoding="utf-8")

api_block = re.compile(
    r"""    # Optional, only for debugging purposes\n    volumes:\n      - api_server_logs:/var/log/onyx\n      # Shared volume for persistent document storage \(Craft file-system mode\)\n      - file-system:/app/file-system(?:\n      # Bind-mount the backend source so code edits apply without rebuilding the image\.\n      - ../../backend:/app)*\n""",
    re.M,
)
background_block = re.compile(
    r"""    # Optional, only for debugging purposes\n    volumes:\n      - background_logs:/var/log/onyx\n      # Shared volume for persistent document storage \(Craft file-system mode\)\n      - file-system:/app/file-system(?:\n      # Bind-mount the backend source so code edits apply without rebuilding the image\.\n      - ../../backend:/app)*\n""",
    re.M,
)
mcp_block = re.compile(
    r"""    # Optional, only for debugging purposes\n    volumes:\n      - mcp_server_logs:/var/log/onyx(?:\n      # Bind-mount the backend source so code edits apply without rebuilding the image\.\n      - ../../backend:/app)*\n""",
    re.M,
)

api_clean = (
    "    # Optional, only for debugging purposes\n"
    "    volumes:\n"
    "      - api_server_logs:/var/log/onyx\n"
    "      # Shared volume for persistent document storage (Craft file-system mode)\n"
    "      - file-system:/app/file-system\n"
    "      # Bind-mount the backend source so code edits apply without rebuilding the image.\n"
    "      - ../../backend:/app\n"
)
background_clean = (
    "    # Optional, only for debugging purposes\n"
    "    volumes:\n"
    "      - background_logs:/var/log/onyx\n"
    "      # Shared volume for persistent document storage (Craft file-system mode)\n"
    "      - file-system:/app/file-system\n"
    "      # Bind-mount the backend source so code edits apply without rebuilding the image.\n"
    "      - ../../backend:/app\n"
)
mcp_clean = (
    "    # Optional, only for debugging purposes\n"
    "    volumes:\n"
    "      - mcp_server_logs:/var/log/onyx\n"
    "      # Bind-mount the backend source so code edits apply without rebuilding the image.\n"
    "      - ../../backend:/app\n"
)

text = api_block.sub(api_clean, text, count=1)
text = background_block.sub(background_clean, text, count=1)
text = mcp_block.sub(mcp_clean, text, count=1)
compose.write_text(text, encoding="utf-8")
PY
