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
from telegram.ext import ApplicationBuilder, filters, MessageHandler, CommandHandler, ContextTypes

import config
import utils

logger = logging.getLogger('bot')


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

    with open('today.csv', 'w') as csvfile:
        file_write = csv.writer(csvfile)
        msg_write = [[date_str]]

        result = requests.get(api_url)
        data_json = result.json()

        for index, element in enumerate(data_json, start=1):
            msg_write.append([f"{index}. {__get_price(element)}"])

        file_write.writerows(msg_write)
    return True


def command_cheapest(update, context):
    logger.info('Bot asked to execute /cheapest command')
    utc_now = datetime.datetime.utcnow()
    date_str = utc_now.strftime('%d/%m/%Y')
    msg = []

    try:
        with open('today.csv') as csvfile:
            file_read = csv.reader(csvfile)
            file_date = next(file_read)[0]
            msg = [f"<pre>Hoy {file_date}</pre>"]

            if file_date == date_str:
                msg = __get_price_data_from_file(file_reader=file_read, message=msg)
            else:
                raise FileNotFoundError
    except FileNotFoundError:
        __update_cache_file_with_cheapest(date_str)

        with open('today.csv') as csvfile:
            file_read = csv.reader(csvfile)
            file_date = next(file_read)[0]
            msg = [f"<pre>Hoy {file_date}</pre>"]  # ignore first line
            msg = __get_price_data_from_file(file_reader=file_read, message=msg)

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f"{linesep}".join(msg),
        parse_mode=telegram.ParseMode.HTML
    )


async def command_help(update, context):
    logger.info('Received command /help')
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Comandos disponibles:\n"
             " - /start - Comienza a interactuar con el bot\n"
             " - /help - Mostrar las interacciones disponibles\n"
             " - /status - Mostrar el estado del bot\n"
    )


def command_start(update, context):
    logger.info('Received command /start')
    context.bot.send_message(chat_id=update.message.chat_id, text=settings.BOT_GREETING)


def command_status(update, context):
    logger.info('bot asked to execute /status command')
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=f'Status is OK, running since {utils.since()}',
    )


def welcome(update: Update, context):
    logger.info('Received new user event')
    new_member = update.message.new_chat_members[0]

    logger.info(f'Waiting {config.WELCOME_DELAY} seconds until user completes captcha...')
    sleep(config.WELCOME_DELAY)
    membership_info = context.bot.get_chat_member(update.message.chat_id, new_member.id)
    if membership_info['status'] == 'left':
        logger.info(f'Skipping welcome message, user {new_member.name} is no longer in the chat')
        return

    logger.info(f'send welcome message for {new_member.name}')
    msg = None

    if new_member.is_bot:
        msg = f"{new_member.name} is a *bot*!! " \
              "-> It could be kindly removed 🗑"
    else:
        if utils.is_bot(new_member):
            context.bot.delete_message(update.message.chat_id,
                                       update.message.message_id)
            if context.bot.kick_chat_member(update.message.chat_id, new_member.id):
                msg = (f"*{new_member.username}* has been banned because I "
                       "considered it was a bot. ")
        else:
            msg = f"Welcome {new_member.name}!! " \
                   "I am a friendly and polite *bot* 🤖"
    if msg:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=msg,
            parse_mode=telegram.ParseMode.MARKDOWN
        )


async def reply(update, _context):
    if not config.bot_replies_enabled():
        return

    msg = update.message.text
    reply_spec = utils.triggers_reply(msg) if msg else None
    if reply_spec is not None:
        logger.info(f'bot sends reply {reply_spec.reply}')
        await update.message.reply_text(reply_spec.reply)


def main():
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    )
    logger.info('Starting bot...')
    config.log(logger.info)
    app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', command_start))
    app.add_handler(CommandHandler('help', command_help))
    app.add_handler(CommandHandler('status', command_status))
    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, reply))
    app.add_handler(CommandHandler('cheapest', command_cheapest))

    logger.info('Bot is ready')
    app.run_polling(allowed_updates=Update.ALL_TYPES,
                    poll_interval=config.POLL_INTERVAL)


if __name__ == "__main__":
    main()
