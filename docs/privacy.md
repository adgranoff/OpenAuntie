# Privacy Policy

## What Data OpenAuntie Stores

OpenAuntie stores family data locally in the `family_data/` directory on your device. This includes:

- **Family profile**: Names, dates of birth, temperament notes, strengths, challenges
- **Behavior data**: Points, chores, consequences, rewards
- **Routine data**: Routine definitions, completion logs
- **Health data**: Medications, appointments, growth records
- **Education data**: Reading logs, homework entries, learning goals
- **Emotional data**: Mood entries, conflict records, developmental milestones
- **Activity data**: Family events, trip plans
- **Financial data**: Allowance config, transactions, savings goals
- **Journal entries**: Free-form parenting observations

## What About the AI Platform?

Your family's stored data (points, routines, health records) is saved as files on your device. OpenAuntie itself never uploads these files.

However, when you chat with an AI like Claude or ChatGPT, your conversation messages are processed by that AI provider — including any family context that OpenAuntie includes to give you personalized advice. With the full tracking setup (Claude Desktop), OpenAuntie may include relevant data snippets (like "M earned 2 points today" or "bedtime routine completion was 80% this week") in the conversation sent to the AI. With the ChatGPT-only setup, only what you type yourself is sent.

This is the same as any other AI chat. For maximum privacy, use nicknames and avoid sharing sensitive medical details in conversation.

## Where Data Is Stored

OpenAuntie stores all family data as JSON files in `family_data/` within the project directory on your device.

- OpenAuntie does not independently upload, sync, or transmit your data files
- No analytics or telemetry is collected by OpenAuntie
- No cookies or tracking of any kind
- With the full tracking setup (Claude Desktop), relevant data snippets may be included in conversation messages sent to your AI provider to give personalized advice
- With the ChatGPT-only setup, only what you type yourself is sent to OpenAI
- Conversation messages are always processed by your AI provider (Anthropic for Claude, OpenAI for ChatGPT) per their privacy policies

## How to Delete Your Data

**On Windows:** Open File Explorer, navigate to your OpenAuntie folder, and delete the `family_data` folder.

**On Mac:** Open Finder, navigate to your OpenAuntie folder, and move the `family_data` folder to the Trash.

<details>
<summary>Command line (advanced)</summary>

```bash
rm -rf family_data/
```

Or delete specific data:
```bash
rm family_data/behavior.json
```
</details>

## How to Export Your Data

Your data is stored as plain text files (JSON format) that you can open in any text editor. To back everything up, just copy the entire `family_data` folder to a USB drive, cloud storage, or another location.

<details>
<summary>Command line (advanced)</summary>

```bash
uv run parenting export > backup.json
```
</details>

## Data Portability

Since all data is plain JSON, you can:

- Back it up to any storage service
- Move it between devices by copying `family_data/`
- Write scripts to process or analyze your data
- Import it into other tools

## Multi-Device and Sharing

**v1 of OpenAuntie is designed for single-device, single-family use.** It does not include:

- Multi-device synchronization
- Cloud storage or backup
- Shared access between co-parents
- Authentication or access control

If multiple people need access, they should use the same device or manually share the `family_data/` directory. Multi-device and co-parenting support is planned for future versions.

## Children's Privacy

OpenAuntie takes children's privacy seriously:

- Behavioral data is private to the family — never displayed publicly or competitively
- OpenAuntie does not share data with schools, employers, or other third parties (though conversation messages are processed by your AI provider as described above)
- Parents control all data and can delete it at any time
- No photos, biometrics, or location data is collected
