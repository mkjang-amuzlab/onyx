from __future__ import annotations

import sys
import types
from typing import Any


def _install_fastmcp_stubs() -> None:
    if "fastmcp" not in sys.modules:
        fastmcp = types.ModuleType("fastmcp")

        class _FastMCP:
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                self.args = args
                self.kwargs = kwargs

            def tool(self, *args: Any, **kwargs: Any):  # noqa: ANN001, ANN201
                def decorator(func):
                    return func

                return decorator

            def http_app(self, *args: Any, **kwargs: Any):  # noqa: ANN001
                class _DummyApp:
                    async def lifespan(self, app):  # noqa: ANN001
                        yield

                    async def __call__(self, scope, receive, send):  # noqa: ANN001
                        return None

                return _DummyApp()

        fastmcp.FastMCP = _FastMCP
        sys.modules["fastmcp"] = fastmcp

    auth_auth = sys.modules.get("fastmcp.server.auth.auth")
    if auth_auth is None:
        auth_auth = types.ModuleType("fastmcp.server.auth.auth")

        class AccessToken:  # noqa: D401
            def __init__(
                self,
                token: str,
                client_id: str | None = None,
                scopes: list[str] | None = None,
                expires_at: Any | None = None,
                resource: Any | None = None,
                claims: dict[str, Any] | None = None,
            ) -> None:
                self.token = token
                self.client_id = client_id
                self.scopes = scopes or []
                self.expires_at = expires_at
                self.resource = resource
                self.claims = claims or {}

        class TokenVerifier:  # noqa: D401
            async def verify_token(self, token: str):  # noqa: ANN201
                return None

        auth_auth.AccessToken = AccessToken
        auth_auth.TokenVerifier = TokenVerifier
        sys.modules["fastmcp.server.auth.auth"] = auth_auth

    dependencies = sys.modules.get("fastmcp.server.dependencies")
    if dependencies is None:
        dependencies = types.ModuleType("fastmcp.server.dependencies")

        def get_access_token():  # noqa: ANN201
            return None

        dependencies.get_access_token = get_access_token
        sys.modules["fastmcp.server.dependencies"] = dependencies

    sys.modules.setdefault("fastmcp.server", types.ModuleType("fastmcp.server"))
    sys.modules.setdefault("fastmcp.server.auth", types.ModuleType("fastmcp.server.auth"))


def _install_onyx_api_stub() -> None:
    if "onyx.mcp_server.api" in sys.modules:
        return

    api_module = types.ModuleType("onyx.mcp_server.api")

    class _DummyMCPServer:
        def tool(self, *args: Any, **kwargs: Any):  # noqa: ANN001, ANN201
            def decorator(func):
                return func

            return decorator

    api_module.mcp_server = _DummyMCPServer()
    sys.modules["onyx.mcp_server.api"] = api_module


_install_fastmcp_stubs()
_install_onyx_api_stub()
