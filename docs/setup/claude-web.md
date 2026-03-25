# Setting Up OpenAuntie with Claude Web (claude.ai)

## How It Works

Claude's web interface supports **Connectors** — remote MCP servers connected via OAuth. This means you can use OpenAuntie's tracking tools directly in the claude.ai web interface.

**However, this requires hosting the MCP server remotely.** This is a more advanced setup.

## Option 1: Use Claude Desktop Instead (Recommended)

If you want the full OpenAuntie experience without hosting, use [Claude Desktop](claude-desktop.md) instead. It runs the MCP server locally on your computer.

## Option 2: Custom Connector (Advanced)

If you've deployed OpenAuntie as a remote MCP server:

1. Go to [claude.ai](https://claude.ai)
2. Click the **+** button in the chat input area
3. Select **Connectors**
4. Click **Add custom connector** at the bottom
5. Enter your server's URL
6. Configure OAuth credentials under **Advanced settings** if required
7. Click **Add**

The parenting tools will appear in your connector list.

## Hosting Options

To make OpenAuntie available as a remote MCP server, you would need to:

1. Deploy the MCP server on a cloud provider (AWS, GCP, Azure, etc.)
2. Add an HTTP transport layer (the default is stdio for local use)
3. Add authentication (the local version has no auth since data stays on-device)

This is not yet supported out of the box. If there's community interest, we'll add a remote deployment guide.
