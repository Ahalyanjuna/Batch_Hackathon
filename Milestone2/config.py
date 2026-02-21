MODE = "REAL"   

#only if mode = real
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/XXXX"
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1474687389879242875/u8DQ7gjgCTJv3ZiamWNALszEvFyUcHnZ2VY5pHBoluLgKy01lq8qf_x6W_91xfHBm8Wx"

#if mode = mock ( local FastAPI endpoint)
MOCK_WEBHOOK_URL = "http://localhost:8000/mock_webhook/slack"