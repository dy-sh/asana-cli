# Asana Project Progress Tracker

A Python script that displays progress bars for all your Asana projects in the console, showing completion percentage based on completed vs total tasks.

## Features

- 🔍 Fetches all projects from all workspaces
- 📊 Displays progress bars with completion percentages
- 📋 Shows task counts (completed/total)
- 🏷️ Indicates project status (Active, Completed, Archived)
- 📈 Provides summary statistics
- 🎨 Beautiful console output with colors and formatting

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Asana API Key

1. Go to [Asana Developer Console](https://app.asana.com/0/developer-console)
2. Create a new app or use an existing one
3. Copy your Personal Access Token

### 3. Set API Key

**Option A: Environment Variable (Recommended)**
```bash
# Windows
set ASANA_API_KEY=your_api_key_here

# Linux/Mac
export ASANA_API_KEY=your_api_key_here
```

**Option B: Command Line Argument**
```bash
python asana_progress.py your_api_key_here
```

## Usage

Run the script:
```bash
python asana_progress.py
```

## Output

The script will display:
- A table with all projects showing:
  - Project name
  - Workspace
  - Visual progress bar with percentage
  - Task count (completed/total)
  - Project status
- Summary statistics including:
  - Total projects
  - Active/Completed/Archived projects
  - Overall progress across all projects

## Example Output

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Asana Projects Progress                           │
├──────────────────────────┬──────────────────┬────────────────────────┬──────┤
│ Project Name             │ Workspace        │ Progress               │ Tasks│
├──────────────────────────┼──────────────────┼────────────────────────┼──────┤
│ Website Redesign         │ Marketing        │ ████████████████████ 100.0% │ 15/15│
│ Mobile App Development   │ Engineering      │ ████████████░░░░░░░░ 60.0%  │ 12/20│
│ Content Creation         │ Marketing        │ ██████░░░░░░░░░░░░░░ 30.0%  │ 3/10 │
└──────────────────────────┴──────────────────┴────────────────────────┴──────┘
```

## Requirements

- Python 3.7+
- Asana API access
- Required packages: `asana`, `tqdm`, `rich`

## Troubleshooting

- **API Key Error**: Make sure your Asana API key is valid and has the necessary permissions
- **No Projects Found**: Check that you have access to projects in your Asana workspaces
- **Connection Issues**: Verify your internet connection and Asana API status 