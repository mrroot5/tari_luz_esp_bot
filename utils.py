import functools
import random
import re
import typing
from typing import Tuple

from telegram import User
import config


def is_chinese(c):
    """
    Returns True if the character passed as parameter is a Chinese one
    """
    num = ord(c)
    return any((
        0x2E80 <= num <= 0x2FD5,
        0x3190 <= num <= 0x319F,
        0x3400 <= num <= 0x4DBF,
        0x4E00 <= num <= 0x9FCC,
        0x6300 <= num <= 0x77FF,
        ))


def too_much_chinese_chars(s):
    letters = list(s)
    num_chinese_chars = sum([is_chinese(c) for c in letters])
    percent = num_chinese_chars / len(letters)
    return percent > config.MAX_CHINESE_CHARS_PERCENT  # More than allowed
                                                       # chars are Chinese


def is_valid_name(user: User):
    return len(user.first_name) <= config.MAX_HUMAN_USERNAME_LENGTH


def is_tgmember_sect(first_name: str):
    return "tgmember.com" in first_name.lower()


def is_bot(user: User):
    """
    Returns True if a new user is a bot. So far only the length of the
    username is checked. In the future, we can add more conditions and use a
    score/weight of the probability of being a bot.

    :param user: The new User
    :type user: User
    :return: True if the new user is considered a bot (according to our rules)
    :rtype: bool
    """
    # Add all the checks that you consider necessary
    return any((
        not is_valid_name(user),
        too_much_chinese_chars(user.first_name),
        is_tgmember_sect(user.first_name),
        ))


@functools.lru_cache()
def get_reply_regex(trigger_words: Tuple[str]):
    """
    Build a regex to match on the trigger words
    """
    pattern = "|".join([fr"\b{word}\b" for word in trigger_words])
    return re.compile(pattern, re.I)


def bot_wants_to_reply() -> bool:
    return random.random() < config.VERBOSITY


class BotReplySpec(typing.NamedTuple):
    message: str
    trigger: str
    reply: str


def triggers_reply(message: str) -> typing.Optional[BotReplySpec]:
    for trigger_words, bot_reply in config.REPLIES.items():
        regex = get_reply_regex(trigger_words)
        match = regex.search(message)
        if match is not None and bot_wants_to_reply():
            # When a match is found, check if the bot will reply based on its
            # reply likelihood
            if not isinstance(bot_reply, str):
                # If value is a list then pick random string from multiple values:
                bot_reply = random.choice(bot_reply)
            return BotReplySpec(message, match.group(0), bot_reply)
    return None
