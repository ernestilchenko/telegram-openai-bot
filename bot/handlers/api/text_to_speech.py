from typing import Literal

import aiofiles.os
import openai
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from bot.config import client
from ...states.state import StateTextToSpeech

router_text_to_speech = Router()


async def generate_text_to_speech(prompt: str, model: str, file_id: str,
                                  voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]) -> str:
    """
    This function generates speech from text based on the provided prompt, model, and voice.

    Parameters:
    prompt (str): The text to be converted to speech.
    model (str): The model to be used for text to speech conversion. It can be "tts-1" or "tts-1-hd".
    file_id (str): The id of the file where the generated speech will be saved.
    voice (Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]): The voice to be used for the speech. It can be "alloy", "echo", "fable", "onyx", "nova", or "shimmer".

    Returns:
    str: If an error occurs during text to speech conversion, it returns a string starting with "Error:" followed by the error message.
    """
    try:
        # Define the path of the speech file
        speech_file_path = file_id
        # Generate the speech using the OpenAI API
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=prompt
        )
        # Save the generated speech to the file
        response.stream_to_file(speech_file_path)
    except openai.OpenAIError as e:
        # If an error occurs, return the error message
        return f"Error: {str(e)}"


@router_text_to_speech.callback_query(F.data == "text_to_speech")
async def text_to_speech(call: types.CallbackQuery, l10n: FluentLocalization) -> None:
    """
    This function handles the "text_to_speech" callback query. It edits the message text and provides a keyboard for
    text to speech related options.
    """
    buttons = [
        [types.InlineKeyboardButton(text=l10n.format_value("tts-1"), callback_data="tts-1")],
        [types.InlineKeyboardButton(text=l10n.format_value("tts-1-hd"), callback_data="tts-1-hd")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.edit_text(text=l10n.format_value("text_text_to_speech"), reply_markup=keyboard)


@router_text_to_speech.callback_query(F.data.startswith("tts"))
async def tts(call: types.CallbackQuery, state: FSMContext, l10n: FluentLocalization) -> None:
    buttons = [
        [types.InlineKeyboardButton(text=l10n.format_value("alloy"), callback_data="alloy"),
         types.InlineKeyboardButton(text=l10n.format_value("echo"), callback_data="echo")],
        [types.InlineKeyboardButton(text=l10n.format_value("fable"), callback_data="fable"),
         types.InlineKeyboardButton(text=l10n.format_value("onyx"), callback_data="onyx")],
        [types.InlineKeyboardButton(text=l10n.format_value("nova"), callback_data="nova"),
         types.InlineKeyboardButton(text=l10n.format_value("shimmer"), callback_data="shimmer")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.edit_text(text=l10n.format_value("text_enter_voice"), reply_markup=keyboard)
    await state.update_data(model=call.data)
    await state.set_state(StateTextToSpeech.text_to_speech)


@router_text_to_speech.callback_query(StateTextToSpeech.text_to_speech)
async def text_to_speech(call: types.CallbackQuery, state: FSMContext, l10n: FluentLocalization) -> None:
    """
    This function handles the message in the "text_to_speech" state. It updates the state with the voice model from
    the callback query data.
    """
    voice_model = call.data
    await call.message.answer(text=l10n.format_value("text_enter_to_speech"))
    await state.update_data(voice_model=voice_model)
    await state.set_state(StateTextToSpeech.text)


# Function to create an empty file
async def create_file_async(user_id, message_id) -> None:
    """
    This function creates an empty file with the given user id and message id in the file name.
    """
    file_name = f"media/{user_id}{message_id}.mp3"
    async with aiofiles.open(file_name, mode='wb') as file:
        await file.write(b'')


@router_text_to_speech.message(StateTextToSpeech.text)
async def text(msg: types.Message, state: FSMContext, l10n: FluentLocalization) -> None:
    """
    This function handles the message in the "text" state. It generates speech from the message text using the model and voice model stored in the state,
    and sends this speech as a voice message. If an error occurs during text to speech conversion, it sends a message with the error.
    """
    prompt = msg.text
    data = await state.get_data()
    mesg = await msg.answer(text=l10n.format_value("text_wait"))
    await create_file_async(msg.from_user.id, msg.message_id)
    await generate_text_to_speech(prompt=prompt, voice=data["voice_model"], model=data["model"],
                                  file_id=f"media/{msg.from_user.id}{msg.message_id}.mp3")
    await mesg.delete()
    await msg.bot.send_voice(chat_id=msg.from_user.id,
                             voice=types.FSInputFile(f"media/{msg.from_user.id}{msg.message_id}.mp3"),
                             )
    await aiofiles.os.remove(f"media/{msg.from_user.id}{msg.message_id}.mp3")
