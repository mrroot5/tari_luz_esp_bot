# Tari luz esp bot

Telegram Bot made in Python to get Spain light rates.

![bot-pic](tari-luz-esp-bot.jpg)

> Image by [rawpixel.com on Freepik](https://www.freepik.com/free-vector/illustration-light-bulb-icon_3207916.htm).

## Installation

Create virtualenv for Python3 and install dependencies:

```shell
python3.12 -m venv venv
```

```shell
pip install -r requirements.txt
```

Next step is to set your bot token for development:

```shell
echo 'TELEGRAM_BOT_TOKEN = "<token of your dev bot>"' > .env
```

Now you can launch the bot with:

```shell
python bot.py
```
