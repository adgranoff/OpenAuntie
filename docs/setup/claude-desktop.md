# Setting Up OpenAuntie with Claude Desktop

**Recommended for the full OpenAuntie experience (tracking + advice). Requires installing some software.** It takes about 15-20 minutes the first time.

> **Note:** This involves installing some software and editing a config file. If that sounds intimidating, try the [ChatGPT option](chatgpt.md) instead — it's easier.

## What You'll Need

- A computer (Mac or Windows)
- An internet connection
- A free Claude account

## Step 1: Install Claude Desktop

1. Go to [claude.ai/download](https://claude.ai/download)
2. Download the installer for your computer (Mac or Windows)
3. Run the installer and follow the prompts
4. Open Claude Desktop and sign in with your Anthropic account

## Step 2: Install UV (Python Package Manager)

UV is a tool that runs OpenAuntie. You only need to install it once.

**On Mac:**
Open Terminal (search for "Terminal" in Spotlight) and paste:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:**
Open PowerShell (search for "PowerShell" in the Start menu) and paste:
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen your terminal/PowerShell after installing.

## Step 3: Download OpenAuntie

**Option A: If you have Git installed:**
```
git clone https://github.com/adgranoff/OpenAuntie.git
```

**Option B: Download as ZIP:**
1. Go to the OpenAuntie GitHub page
2. Click the green "Code" button
3. Click "Download ZIP"
4. Unzip the file to a folder you'll remember (e.g., your Documents folder)

Remember where you put it! You'll need the path in the next step.

## Step 4: Connect OpenAuntie to Claude Desktop

This step tells Claude Desktop where to find OpenAuntie. You will edit a small configuration file — it sounds technical, but just follow along.

1. Open Claude Desktop
2. Go to **Settings** (gear icon in the top left)
3. Click **Developer**
4. Click **Edit Config** — this will open a text file in your default text editor

5. **Look at what's in the file:**
   - If the file is empty, or contains just `{}`, that's normal — it means no tools are connected yet
   - Select everything in the file and delete it

6. **Paste the following text** into the file (replacing everything that was there):

**On Mac:**
```json
{
  "mcpServers": {
    "parenting": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/YOUR_USERNAME/openauntie", "python", "-m", "mcp_server.run_server"]
    }
  }
}
```

**On Windows:**
```json
{
  "mcpServers": {
    "parenting": {
      "command": "uv",
      "args": ["run", "--directory", "C:/Users/YOUR_USERNAME/Documents/openauntie", "python", "-m", "mcp_server.run_server"]
    }
  }
}
```

7. **Replace the folder path** with the actual location where you put OpenAuntie:
   - **On Windows:** Open File Explorer, navigate to the OpenAuntie folder, and click in the address bar at the top — it will show the full path (something like `C:\Users\Sarah\Documents\OpenAuntie`). Copy that path and paste it into the config, replacing `C:/Users/YOUR_USERNAME/Documents/openauntie`. Use forward slashes (`/`) instead of backslashes (`\`).
   - **On Mac:** Open Finder, navigate to the OpenAuntie folder, right-click the folder, hold the Option key, and click **Copy as Pathname**. Paste that path into the config, replacing `/Users/YOUR_USERNAME/openauntie`.

8. **Save the file** (Ctrl+S on Windows, Cmd+S on Mac)
9. **Completely quit and restart Claude Desktop** — not just close the window, but fully quit the app (right-click the icon in your taskbar/dock and choose Quit)

## Step 5: Verify It Works

After restarting Claude Desktop, you should see a hammer icon in the chat input area. This means the tools are connected!

If you click the hammer, you should see tools starting with "parenting_".

## Step 6: Set Up Your Family

In Claude Desktop, say:

> "Help me set up my family profile. My family name is [your name], I'm [your name], and I have [number] kids: [names and birthdays]."

OpenAuntie will create your family profile and you're ready to go!

## What to Try First

Here are some things to say to Claude with OpenAuntie connected:

- **"My 7-year-old won't do homework without a fight. What should I do?"** — Get evidence-based advice personalized to your child's age
- **"Set up a point system with 3 points per day"** — Create a behavior tracking system
- **"Create a bedtime routine with 5 steps"** — Build a routine tracker
- **"How's our week going?"** — Get a weekly summary across all domains
- **"Create a family meeting agenda"** — Auto-generate an agenda from your family's data

## Troubleshooting

**No hammer icon appears:**
- Make sure you completely restarted Claude Desktop (quit + reopen)
- Check that the file path in the config matches where you downloaded OpenAuntie
- Make sure UV is installed: open a terminal and type `uv --version`

**"Server failed to start" error:**
- Open a terminal, navigate to the OpenAuntie folder, and run: `uv run python -m mcp_server.run_server`
- If you see errors, they'll tell you what's wrong

**Tools don't appear:**
- Click the hammer icon — you should see a list of tools starting with "parenting_"
- If the list is empty, check the Claude Desktop logs (Help > Show Logs)
