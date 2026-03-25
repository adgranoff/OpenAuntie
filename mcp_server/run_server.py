"""Entry point for the OpenAuntie MCP server (stdio transport)."""

from mcp_server.server import mcp


def main() -> None:
    """Run the MCP server in stdio mode."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
