# Poltergeist

> *"Gotta stop dat King Boo, 'cause he broke up the whole Dark Moon dude!"*
> ~ **Prof. E. Gadd**, on the mission ahead

**Poltergeist** is the notification and messaging hub for the Evershade ecosystem. It sends notifications to Slack, Discord, email, and Telegram, replacing scattered webhook handlers with a unified system.

**Luigi's Mansion origin:** *Poltergeist* ~ the ancient ghosts from Luigi's Mansion: Dark Moon that cause disturbances and ruckuses, perfect for sending notifications.

## Features

- **Multi-channel** ~ Slack, Discord, email, Telegram
- **Templates** ~ Notification templates with variables
- **Queues** ~ Async delivery with retry logic

## Quick Start

```bash
docker compose up -d Poltergeist
pip install -e ".[dev]"
python -m uvicorn poltergeist.api:app --host 0.0.0.0 --port 8088
```

## API

- **Swagger UI:** `http://localhost:8088/docs`
- **ReDoc:** `http://localhost:8088/redoc`

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | `Poltergeist-dev-key-change-me` | API authentication key |
| `PORT` | `8088` | Server port |

## License

MIT

**Repo:** [LukaG712/Poltergeist](https://github.com/LukaG712/Poltergeist)

---

> **Disclaimer:** This project is a fan-made, independent software project. It is not affiliated with, endorsed by, or in any way connected to Nintendo, Next Level Games, or any of their subsidiaries. All Luigi's Mansion trademarks and character names are property of their respective owners. Service names are used purely for thematic inspiration.
