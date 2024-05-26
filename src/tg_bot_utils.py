"""This module contains utility functions and classes for the chatbot."""

import json
from typing import Any, Dict, List

import openai
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tg_bot_settings import BOT_HISTORY_LENGTH, BOT_TOKEN, MODEL_NAME

SYSTEM_PROMPT = (
    'You are a helpful assistant that provides useful information to the user. '
    'Your name is Claudia. You are friendly and cheerful. You use The International System of Units.')


def load_config() -> Dict[str, Any]:
    """
    Load the configuration from the 'credentials.json' file.

    Returns:
        dict: The loaded configuration.
    """
    with open("credentials.json") as config_file:
        return json.load(config_file)


# Setup bot and API key
config = load_config()
openai.api_key = config["openai_api_key"]

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class MessageHistory:
    """Represent a message history."""

    def __init__(self):
        """Initialize a new instance of the MessageHistory class."""
        self.history: List[Dict[str, str]] = []

    def add_message(self, message: Dict[str, str]) -> None:
        """
        Add a message to the history.

        Args:
            message (Dict[str, str]): The message to add.
        """
        self.history.append(message)

    def clear(self) -> None:
        """Clear the message history."""
        self.history = []

    def history(self) -> List[Dict[str, str]]:
        """
        Return the message history.

        Returns:
            List[Dict[str, str]]: The message history.
        """
        return self.history[-BOT_HISTORY_LENGTH:]


class Form(StatesGroup):
    """Represent a form for handling states in the chatbot."""

    start_chat = State()


async def get_chatgpt_response(history: List[Dict[str, str]]) -> str:
    """
    Generate a response from the ChatGPT model based on the given conversation history.

    Args:
        history (List[Dict[str, str]]): The conversation history, where each element is a dictionary
            with 'role' and 'content' keys representing the role of the speaker and the content of their message.

    Returns:
        str: The generated response from the ChatGPT model.

    Raises:
        None

    """
    formatted_history = [{"role": hist["role"], "content": hist["content"]} for hist in history]
    client = openai.AsyncOpenAI(api_key=openai.api_key)
    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=formatted_history,
    )
    if response.choices[0].message.content:
        return response.choices[0].message.content
    return "No response from the model."


async def welcome(message: types.Message, state: FSMContext):
    """
    Send a welcome message to the user and displays a keyboard with options.

    Args:
        message (types.Message): The incoming message from the user.
        state (FSMContext): The state of the conversation.

    Returns:
        None
    """
    await state.reset_state(with_data=False)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Start Chat", callback_data="start_chat"))
    keyboard.add(InlineKeyboardButton("Help", callback_data="help"))
    await message.answer("Hi! I am your Personal AI assistant. How can I assist you today?", reply_markup=keyboard)

    return


@dp.callback_query_handler(lambda command: command.data == "start_chat")
async def process_start_chat(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Process the 'start_chat' callback query.

    Args:
        callback_query (types.CallbackQuery): The callback query object.
        state (FSMContext): The FSM context object.

    Returns:
        None
    """
    await state.set_state(Form.start_chat)
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "You can start chatting now! Just type your message.")

    return


@dp.callback_query_handler(lambda command: command.data == "help")
async def process_help(callback_query: types.CallbackQuery):
    """
    Process the 'help' callback query.

    Args:
        callback_query (types.CallbackQuery): The callback query object.

    Returns:
        None
    """
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Here’s some help...")

    return


@dp.message_handler(state=Form.start_chat)
async def handle_message(message: types.Message, state: FSMContext) -> None:
    """
    Handle incoming messages from the user and generates a response using ChatGPT.

    Args:
        message (types.Message): The incoming message from the user.
        state (FSMContext): The state of the conversation.

    Returns:
        None
    """
    state_data = await state.get_data()

    message_history = state_data.get("history", [{"role": "system", "content": SYSTEM_PROMPT}])
    message_history.append({"role": "user", "content": message.text})

    gpt_response = await get_chatgpt_response(message_history)
    message_history.append({"role": "assistant", "content": gpt_response})

    await state.update_data(history=message_history)
    await message.answer(gpt_response)
    return None
