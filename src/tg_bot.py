"""This module contains the main function for the Telegram bot."""

from aiogram import executor

from tg_bot_utils import (
    Form,
    dp,
    handle_message,
    process_help,
    process_start_chat,
    welcome,
)


def main() -> None:
    """
    Entry point of the program. Registers message handlers and starts the polling executor.

    Returns:
        None

    """
    dp.register_message_handler(welcome, commands=["start"])
    dp.register_callback_query_handler(process_start_chat, lambda command: command.data == "start_chat", state="*")
    dp.register_callback_query_handler(process_help, lambda command: command.data == "help", state="*")
    dp.register_message_handler(handle_message, state=Form.start_chat)

    executor.start_polling(dp, skip_updates=True)

    return None


if __name__ == "__main__":
    main()
