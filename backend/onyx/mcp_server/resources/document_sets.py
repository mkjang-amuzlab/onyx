"""Resources that expose document set metadata for the Onyx MCP server."""

from __future__ import annotations

from typing import Any

from onyx.mcp_server.api import mcp_server
from onyx.mcp_server.utils import get_accessible_document_sets
from onyx.mcp_server.utils import require_access_token
from onyx.utils.logger import setup_logger

logger = setup_logger()


@mcp_server.resource(
    "resource://document_sets",
    name="document_sets",
    description=(
        "Lists the document sets available to the current user in Onyx. "
        "Document sets group documents by project, team, or topic. "
        "Pass one or more set names as `document_set_names` in "
        "`search_indexed_documents` to scope a search to specific groups."
    ),
    mime_type="application/json",
)
async def document_sets_resource() -> dict[str, Any]:
    """Return the list of accessible document set names."""
    access_token = require_access_token()

    try:
        document_sets = await get_accessible_document_sets(access_token)
    except Exception as e:
        logger.error(
            "Onyx MCP Server: Failed to fetch document sets: %s", e, exc_info=True
        )
        return {
            "document_sets": [],
            "error": f"Failed to fetch document sets: {str(e)}",
        }

    names = sorted(ds.name for ds in document_sets if ds.name)
    logger.info(
        "Onyx MCP Server: document_sets resource returning %s entries", len(names)
    )
    return {"document_sets": names}
