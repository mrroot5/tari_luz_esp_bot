from typing import Any, NamedTuple

from prettyconf import config as _config

_config_registry = []


class _ConfigItem(NamedTuple):
    name: str
    value: Any
    suppress_log: bool = False

    def log(self, logger_method, indent=False):
        value = "***PRIVATE***" if self.suppress_log else self.value
        indentation = '   ' if indent else ''
        logger_method(f"{indentation}{self.name} = {value}")


def config(item, cast=lambda v: v, suppress_log=False, **kwargs):
    value = _config(item, cast, **kwargs)
    global _config_registry
    _config_registry.append(_ConfigItem(item, value, suppress_log))
    return value


def log(logger_method):
    logger_method("Bot configuration:")
    for config_item in _config_registry:
        config_item.log(logger_method, indent=True)


TELEGRAM_BOT_TOKEN = config(
    "TELEGRAM_BOT_TOKEN", default="put here the token of your bot", suppress_log=True
)

WEBHOOK_URL = config("WEBHOOK_URL", default="put here the webhook url of your bot")

# Bot message for start command
BOT_GREETING = config('BOT_GREETING', default="Hola! Estoy listo para darte información sobre el\
                      precio de la luz. Usa el comando /help para ver las acciones disponibles.")

REQUESTS_DEFAULT_TIMEOUT = 30
