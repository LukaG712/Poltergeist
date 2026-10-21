# Polterpup

> *"Gotta stop dat King Boo, 'cause he broke up the whole Dark Moon dude!"*
> ~ **Prof. E. Gadd**, on the mission ahead

**Polterpup** is the notification and messaging hub for the Evershade ecosystem. It sends notifications to Slack, Discord, email, and Telegram, replacing scattered webhook handlers with a unified system.

**Luigi's Mansion origin:** *Polterpup* ~ ghost dogs from Luigi's Mansion: Dark Moon that howl and deliver messages.

## Features

- **Multi-channel** ~ Slack, Discord, email, Telegram
- **Templates** ~ Notification templates with variables
- **Queues** ~ Async delivery with retry logic

## Quick Start

```bash
docker compose up -d Polterpup
pip install -e ".[dev]"
python -m uvicorn polterpup.api:app --host 0.0.0.0 --port 8088
```

## API

- **Swagger UI:** `http://localhost:8088/docs`
- **ReDoc:** `http://localhost:8088/redoc`

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | `Polterpup-dev-key-change-me` | API authentication key |
| `PORT` | `8088` | Server port |

## License

MIT
