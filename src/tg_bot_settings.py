"""Settings configuration for the Telegram bot."""

import logging
import os

DEFAULT_HISTOTY_LENGTH = 20
BOT_HISTORY_LENGTH = int(os.getenv("BOT_HISTORY_LENGTH", DEFAULT_HISTOTY_LENGTH))

# Log configuration
logger = logging.getLogger("gpt_chat")
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

# Telegram bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if BOT_TOKEN:
    logger.info("BOT_TOKEN found, starting the bot")
else:
    logger.error("BOT_TOKEN env var not found, cannot start the bot without it. Create it with @BotFather Telegram bot")


DEFAULT_MODEL_NAME = "gpt-3.5-turbo"
MODEL_NAME = os.getenv("MODEL_NAME", DEFAULT_MODEL_NAME)
logger.info(f"Using model: {MODEL_NAME}")
