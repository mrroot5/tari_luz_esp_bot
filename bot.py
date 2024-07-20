"""
# Tarifa luz bot

Command to get spanish light prices.

## Docs

* API: https://api.preciodelaluz.org
"""

import csv
import datetime
import logging
from os import linesep

import requests
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

import config
import utils

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('tari_luz_bot')


async def command_cheapest(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /cheapest command, retrieves the current date, reads data from a CSV file,
    updates the cache file if needed, and sends a message with the cheapest price data in HTML format.

    Parameters:
        update (Update): The update object containing information about the incoming message.
        _context (ContextTypes.DEFAULT_TYPE): Context object containing information about the current state of the bot.
    """
    logger.info('Bot asked to execute /cheapest command')
    utc_now = datetime.datetime.now(datetime.UTC)
    date_str = utc_now.strftime('%d/%m/%Y')
    msg = []

    try:
        with open('today.csv', encoding="utf-8") as csvfile:
            file_read = csv.reader(csvfile)
            file_date = next(file_read)[0]
            msg = [f"<pre>Hoy {file_date}</pre>"]

            if file_date == date_str:
                msg = __get_price_data_from_file(file_reader=file_read, message=msg)
            else:
                raise FileNotFoundError
    except FileNotFoundError:
        __update_cache_file_with_cheapest(date_str)

        with open('today.csv', encoding="utf-8") as csvfile:
            file_read = csv.reader(csvfile)
            file_date = next(file_read)[0]
            msg = [f"<pre>Hoy {file_date}</pre>"]  # ignore first line
            msg = __get_price_data_from_file(file_reader=file_read, message=msg)

    await update.message.reply_text(
        f"{linesep}".join(msg),
        parse_mode=telegram.constants.ParseMode('HTML')
    )


async def command_help(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /help command.

    It sends a message with a list of available commands to the user.

    Parameters:
        update (Update): The update object containing information about the incoming message.
        _context (ContextTypes.DEFAULT_TYPE): Context object containing information about the current state of the bot.

    Returns:
        None
    """
    logger.info('Received command /help')
    await update.message.reply_text(
        "Comandos disponibles:\n"
        " - /start - Comienza a interactuar con el bot\n"
        " - /help - Mostrar las interacciones disponibles\n"
        " - /status - Mostrar el estado del bot\n"
        " - /cheapest - Obtener el precio mas barato de la luz"
    )


async def command_start(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command. It replies with the bot greeting message.

    Parameters:
        update (Update): The update object containing information about the incoming message.
        _context (ContextTypes.DEFAULT_TYPE): Context object containing information about the current state of the bot.

    Returns:
        None
    """
    logger.info('Received command /start')
    await update.message.reply_text(config.BOT_GREETING)


async def command_status(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /status command. It replies with the bot uptime.

    Parameters:
        update (Update): The update object containing information about the incoming message.
        _context (ContextTypes.DEFAULT_TYPE): Context object containing information about the current state of the bot.

    Returns:
        None
    """
    logger.info('bot asked to execute /status command')
    await update.message.reply_text(f'Status is OK, running since {utils.since()}')


async def handle_private_message(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Just tell the use to use commands instead of regular text.

    Args:
        update (Update): The update object containing information about the incoming message.
        _context (ContextTypes.DEFAULT_TYPE): Context object containing information about the current state of the bot.

    Returns:
        None
    """
    await update.message.reply_text('I would be glad to have a conversation with you but I only reply to commands,\
                                    use my /help command to know the options please')


def main():
    """
    A function to initialize the main bot functionality and bot commands.
    """
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    )
    logger.info('Starting bot...')
    config.log(logger.info)
    app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', command_start))
    app.add_handler(CommandHandler('help', command_help))
    app.add_handler(CommandHandler('status', command_status))
    app.add_handler(CommandHandler('cheapest', command_cheapest))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_private_message)
    )

    logger.info('Bot is ready')
    app.run_webhook(
        listen='127.0.0.1',
        port=8080,
        url_path='/',
        webhook_url=config.WEBHOOK_URL
    )


def __get_price(data: dict) -> str:
    price = data.get('price')
    price_kwh = float(price) / 1000 if price else ''

    return f"<b>{data.get('hour', '')}</b>: {price_kwh:.3f} € / kWh."


def __get_price_data_from_file(file_reader, message=None) -> [str]:
    if not message:
        message = []

    for row in file_reader:
        message.append(row[0])

    return message


def __update_cache_file_with_cheapest(date_str: str) -> bool:
    number_of_prices = 5
    api_url = f'https://api.preciodelaluz.org/v1/prices/cheapests?zone=PCB&n={number_of_prices}'

    with open('today.csv', 'w', encoding='utf-8') as csvfile:
        file_write = csv.writer(csvfile)
        msg_write = [[date_str]]

        result = requests.get(api_url, timeout=config.REQUESTS_DEFAULT_TIMEOUT)
        data_json = result.json()

        for index, element in enumerate(data_json, start=1):
            msg_write.append([f"{index}. {__get_price(element)}"])

        file_write.writerows(msg_write)
    return True


if __name__ == "__main__":
    main()
