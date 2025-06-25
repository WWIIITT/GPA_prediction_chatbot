# Discord GPA Prediction Bot Setup Guide

## Requirements

Create a `requirements.txt` file with:
```
discord.py>=2.3.0
numpy>=1.24.0
scikit-learn>=1.3.0
```

## Installation Steps

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Under "Token", click "Copy" to get your bot token
6. Replace `'YOUR_BOT_TOKEN_HERE'` in the code with your actual token

### 3. Set Bot Permissions

1. In the Developer Portal, go to "OAuth2" → "URL Generator"
2. Select these scopes:
   - `bot`
   - `applications.commands`
3. Select these bot permissions:
   - Send Messages
   - Embed Links
   - Read Message History
   - Use Slash Commands
4. Copy the generated URL and use it to invite the bot to your server

### 4. Run the Bot
```bash
python gpa_bot.py
```

## Features

### 📊 GPA Calculation
- **Simple GPA**: Calculate GPA from letter grades
  - Example: `!calculate A B+ A- C+`
- **Weighted GPA**: Calculate with credit hours
  - Example: `!calculate_weighted A,3 B+,4 A-,3`

### 📈 GPA Tracking
- **Add GPA**: Track semester GPAs
  - Example: `!add_gpa 3.5 Fall2023`
- **View History**: See all your GPAs
  - Example: `!history`
- **Statistics**: Get detailed analysis
  - Example: `!stats`

### 🔮 GPA Prediction
- **Predict Future GPA**: Uses linear regression to predict trends
  - Example: `!predict`
- Requires at least 2 semesters of data
- Provides trend analysis and recommendations

### 🎯 Commands Overview

| Command | Description | Example |
|---------|-------------|---------|
| `!help_gpa` | Show all commands | `!help_gpa` |
| `!calculate` | Calculate GPA from grades | `!calculate A B+ C` |
| `!calculate_weighted` | Calculate weighted GPA | `!calculate_weighted A,3 B,4` |
| `!add_gpa` | Add GPA to history | `!add_gpa 3.5 Spring2024` |
| `!history` | View GPA history | `!history` |
| `!predict` | Predict future GPA | `!predict` |
| `!stats` | View detailed statistics | `!stats` |
| `!clear` | Clear all data | `!clear` |

## Grade Scale

| Letter | GPA |
|--------|-----|
| A+, A  | 4.0 |
| A-     | 3.7 |
| B+     | 3.3 |
| B      | 3.0 |
| B-     | 2.7 |
| C+     | 2.3 |
| C      | 2.0 |
| C-     | 1.7 |
| D+     | 1.3 |
| D      | 1.0 |
| D-     | 0.7 |
| F      | 0.0 |

## Data Storage

- User data is stored locally in `gpa_data.json`
- Each user's data is stored separately by Discord user ID
- Data persists between bot restarts

## Customization

### Change Command Prefix
Change `PREFIX = '!'` to your preferred prefix (e.g., `'$'`, `'.'`, etc.)

### Modify Grade Scale
Edit the `GRADE_TO_GPA` dictionary to match your institution's grading scale

### Add Features
- Database integration (PostgreSQL, MySQL)
- Course-specific tracking
- Goal setting and reminders
- Export data to CSV/PDF
- Grade improvement suggestions
- Multi-server support with different configs

## Troubleshooting

### Bot Not Responding
1. Check bot token is correct
2. Ensure bot has proper permissions
3. Verify intents are enabled in Discord Developer Portal

### Import Errors
```bash
pip install --upgrade discord.py numpy scikit-learn
```

### Permission Errors
Make sure the bot has these permissions in your Discord server:
- Send Messages
- Embed Links
- Read Message History

## Security Note

⚠️ **Never share your bot token publicly!** 
- Use environment variables for production
- Add `.env` to `.gitignore` if using git

Example using environment variables:
```python
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
```
