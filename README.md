# PROJECT JARVIS 🤖

An AI-powered voice assistant built with LiveKit Agents and Google Gemini, inspired by the JARVIS AI from Iron Man. Talk to JARVIS naturally using your microphone, and it will respond, execute tasks, and control your computer — all hands-free.

---

## Features

- 🎙️ **Real-time Voice Conversation** — Speak naturally and JARVIS responds instantly using Google Gemini's Live API
- 🌤️ **Weather Lookup** — Ask JARVIS for the weather in any city
- 🔍 **Web Search** — JARVIS can search the web and summarize results for you
- 📧 **Send Emails** — Dictate emails and JARVIS sends them via Gmail
- 🎵 **Play Music** — Ask JARVIS to play any song and it opens it on YouTube

---

## Tech Stack

- [LiveKit Agents](https://github.com/livekit/agents) — Real-time voice agent framework
- [Google Gemini Live API](https://ai.google.dev/) — Realtime multimodal AI model
- [aiohttp](https://docs.aiohttp.org/) — Async HTTP requests
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — YouTube video search
- Python 3.12

---

## Project Structure

```
PROJECT_JARVIS_0.1/
├── agent.py        # Main entry point and agent setup
├── tools.py        # Tool definitions (weather, search, email, music)
├── prompts.py      # Agent and session instructions
├── .env            # Environment variables (not committed)
├── requirements.txt
└── venv/
```

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/PROJECT_JARVIS_0.1.git
cd PROJECT_JARVIS_0.1
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the root directory:
```env
LIVEKIT_URL=wss://your-livekit-url.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
GOOGLE_API_KEY=your_google_api_key
GMAIL_USER=your_gmail@gmail.com
GMAIL_PASS=your_gmail_app_password
```

> **Note:** For `GMAIL_PASS`, use a [Gmail App Password](https://myaccount.google.com/apppasswords), not your regular Gmail password.

### 5. Run JARVIS
```bash
python agent.py console
```

---

## Usage

Once running, just speak to JARVIS:

| What you say | What JARVIS does |
|---|---|
| "What's the weather in New York?" | Fetches current weather |
| "Search for the latest AI news" | Searches the web and summarizes |
| "Send an email to john@gmail.com saying hello" | Sends an email via Gmail |
| "Play Blinding Lights by The Weeknd" | Opens and plays the song on YouTube |

---

## Getting API Keys

| Service | Link |
|---|---|
| Google AI Studio (Gemini) | https://aistudio.google.com/apikey |
| LiveKit Cloud | https://cloud.livekit.io |
| Gmail App Password | https://myaccount.google.com/apppasswords |

---

## License

MIT License — feel free to use and modify for personal projects.

---

*Built with ❤️ — Because everyone deserves their own JARVIS.*
