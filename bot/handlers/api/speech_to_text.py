import aiofiles.os
import openai
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from ...config import client
from ...states.state import StateSpeechToText

# Create a router for speech to text related commands and filters
router_speech_to_text = Router()


async def generate_speech_to_text(model: str, file_path: str) -> str:
    """
    This function generates text from speech based on the provided model and audio file.

    Parameters:
    model (str): The model to be used for speech to text conversion. It can be "whisper-1".
    file_path (str): The path to the audio file to be converted to text.

    Returns:
    str: The text generated from the speech in the audio file. If an error occurs during speech to text conversion, it returns a string starting with "Error:" followed by the error message.
    """
    # Open the audio file in read binary mode
    audio_file = open(file_path, "rb")
    try:
        # Generate the text from speech using the OpenAI API
        response = client.audio.translations.create(
            model=model,
            file=audio_file,
            response_format="text"
        )
        # Return the generated text
        return response
    except openai.OpenAIError as e:
        # If an error occurs, return the error message
        return f"Error: {str(e)}"


# Handler for the "speech_to_text" callback query
@router_speech_to_text.callback_query(F.data == "speech_to_text")
async def speech_to_text(call: types.CallbackQuery, l10n: FluentLocalization) -> None:
    """
    This function handles the "speech_to_text" callback query. It edits the message text and provides a keyboard for speech to text related options.
    """
    button_text_speech_to_text = [
        [types.InlineKeyboardButton(text=l10n.format_value("whisper_1"), callback_data="whisper_1")],
    ]

    # Inline keyboard markup for the speech to text conversion model selection
    keyboard_text_speech_to_text = types.InlineKeyboardMarkup(inline_keyboard=button_text_speech_to_text)
    await call.message.edit_text(text=l10n.format_value("text_speech_to_text"),
                                 reply_markup=keyboard_text_speech_to_text)


# Handler for the "whisper_1" callback query
@router_speech_to_text.callback_query(F.data.startswith("whisper"))
async def whisper_1(call: types.CallbackQuery, state: FSMContext, l10n: FluentLocalization) -> None:
    """
    This function handles the "whisper_1" callback query. It sends a message and updates the state with the model "whisper-1".
    """
    await call.message.edit_text(text=l10n.format_value("text_enter_audio"))
    await state.update_data(model="whisper-1")
    await state.set_state(StateSpeechToText.audio_path)


# Handler for the message in the "audio_path" state
@router_speech_to_text.message(StateSpeechToText.audio_path)
async def audio_path(msg: types.Message, state: FSMContext, l10n: FluentLocalization) -> None:
    """
    This function handles the message in the "audio_path" state. It downloads the voice message, generates text from the speech using the model stored in the state,
    and sends this text as a message. If an error occurs during speech to text conversion, it sends a message with the error.
    """
    voice = msg.voice.file_id
    file = await msg.bot.get_file(file_id=voice)
    file_path = file.file_path
    file_name = f"media/{msg.from_user.id}{voice}.mp3"
    await msg.bot.download_file(file_path, file_name)
    data = await state.get_data()
    mesg = await msg.answer(text=l10n.format_value("text_wait"))
    res = await generate_speech_to_text(file_path=file_name, model=data["model"])
    if res.startswith("Error:"):
        await msg.answer(text=res)
    else:
        await mesg.delete()
        await msg.answer(text=res)
        await aiofiles.os.remove(file_name)
