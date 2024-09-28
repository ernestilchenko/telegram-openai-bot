import base64

import aiofiles.os
import aiohttp
import openai
from aiogram import F, types, Router, flags
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from ...config import client, OPENAI_API
from ...states.state import StateVisionUrl, StateVisionPhoto

# Create a router for vision related commands and filters
router_vision = Router()


async def generate_vision_url(model: str, text: str, url: str) -> str:
    """
    This function generates a vision based on the provided model, text, and URL.

    Parameters:
    model (str): The model to be used for vision generation. It can be "gpt-4-vision-preview".
    text (str): The text to be used for vision generation.
    url (str): The URL of the image to be used for vision generation.

    Returns:
    str: The generated vision. If an error occurs during vision generation, it returns a string starting with "Error:" followed by the error message.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        return response.choices[0].message.content
    except openai.OpenAIError as e:
        return f"Error: {str(e)}"


async def encode_image(image_path) -> str:
    """
    This function encodes an image to base64 format.

    Parameters:
    image_path (str): The path to the image to be encoded.

    Returns:
    str: The base64 encoded image.
    """
    async with aiofiles.open(image_path, "rb") as image_file:
        image_data = await image_file.read()
        return base64.b64encode(image_data).decode('utf-8')


async def generate_vision_file(model: str, text: str, file_path: str) -> str:
    """
    This function generates a vision based on the provided model, text, and image file.

    Parameters:
    model (str): The model to be used for vision generation. It can be "gpt-4-vision-preview".
    text (str): The text to be used for vision generation.
    file_path (str): The path to the image file to be used for vision generation.

    Returns:
    str: The generated vision. If an error occurs during vision generation, it returns a string starting with "Error:" followed by the error message.
    """
    try:
        image_path = file_path
        base64_image = await encode_image(image_path)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API}"
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers,
                                    json=payload) as response:
                response_json = await response.json()
                return response_json['choices'][0]['message']['content']
    except openai.OpenAIError as e:
        return f"Error: {str(e)}"


# Handler for the "vision" callback query
@router_vision.callback_query(F.data == "vision")
async def vision(call: types.CallbackQuery, l10n: FluentLocalization) -> None:
    """
    This function handles the "vision" callback query. It edits the message text and provides a keyboard for vision related options.
    """
    buttons = [
        [types.InlineKeyboardButton(text="👁️ GPT-4 Vision Preview", callback_data="gpt_4_vision_preview")],
    ]

    # Inline keyboard markup for the image vision model selection
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.edit_text(text=l10n.format_value("text_vision"), reply_markup=keyboard)


# Handler for the "gpt_4_vision_preview" callback query
@router_vision.callback_query(F.data == "gpt_4_vision_preview")
async def gpt_4_vision_preview(call: types.CallbackQuery, l10n: FluentLocalization, state: FSMContext) -> None:
    """
    This function handles the "gpt_4_vision_preview" callback query. It sends a message and updates the state with the model "gpt-4-vision-preview".
    """
    buttons = [
        [types.InlineKeyboardButton(text="📤 Upload", callback_data="upload"),
         types.InlineKeyboardButton(text="🔗 Url", callback_data="upload_url")],
    ]

    # Inline keyboard markup for the option selection
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.edit_text(text=l10n.format_value("text_select"), reply_markup=keyboard)
    await state.update_data(model="gpt-4-vision-preview")


# Handler for the "upload" callback query
@router_vision.callback_query(F.data == "upload")
async def upload(call: types.CallbackQuery, l10n: FluentLocalization, state: FSMContext) -> None:
    """
    This function handles the "upload" callback query. It prompts the user to upload a photo and sets the state to "vision_photo".
    """
    await call.message.edit_text(text=l10n.format_value("text_enter_photo"))
    await state.set_state(StateVisionPhoto.vision_photo)


# Handler for the "upload_url" callback query
@router_vision.callback_query(F.data == "upload_url")
async def upload_url(call: types.CallbackQuery, l10n: FluentLocalization, state: FSMContext) -> None:
    """
    This function handles the "upload_url" callback query. It prompts the user to enter a URL and sets the state to "vision_url".
    """
    await call.message.edit_text(text=l10n.format_value("text_enter_url"))
    await state.set_state(StateVisionUrl.vision_url)


# Handler for the message in the "vision_photo" state
@router_vision.message(StateVisionPhoto.vision_photo)
@flags.chat_action("upload_photo")
async def vision_photo(msg: types.Message, l10n: FluentLocalization, state: FSMContext) -> None:
    """
    This function handles the message in the "vision_photo" state. It downloads the photo from the message, stores the file name in the state, and prompts the user to enter text.
    """
    await msg.answer(text=l10n.format_value("text_enter"))
    file_id = msg.photo[-1].file_id
    file = await msg.bot.get_file(file_id=file_id)
    file_path = file.file_path
    file_name = f"media/{msg.from_user.id}{file_id}.jpg"
    await msg.bot.download_file(file_path, file_name)
    await state.update_data(file_name=file_name)
    await state.set_state(StateVisionPhoto.vision_text)


# Handler for the message in the "vision_text" state
@router_vision.message(StateVisionPhoto.vision_text)
async def vision_text(msg: types.Message, l10n: FluentLocalization, state: FSMContext) -> None:
    """
    This function handles the message in the "vision_text" state. It generates a vision from the photo and text using the model stored in the state, and sends this vision as a message.
    If an error occurs during vision generation, it sends a message with the error.
    """
    prompt = msg.text
    data = await state.get_data()
    mesg = await msg.answer(text=l10n.format_value("text_wait"))
    res = await generate_vision_file(model=data["model"], file_path=data["file_name"], text=prompt)
    if res.startswith("Error:"):
        await msg.answer(text=res)
    else:
        await mesg.delete()
        await msg.bot.send_message(chat_id=msg.from_user.id, text=res)
        await aiofiles.os.remove(data["file_name"])


# Handler for the message in the "vision_url" state
@router_vision.message(StateVisionUrl.vision_url)
async def vision_url(msg: types.Message, l10n: FluentLocalization, state: FSMContext) -> None:
    """
    This function handles the message in the "vision_url" state. It stores the URL in the state and prompts the user to enter text.
    """
    await msg.answer(text=l10n.format_value("text_enter"))
    url = msg.text
    await state.update_data(url=url)
    await state.set_state(StateVisionUrl.vision_text)


# Handler for the message in the "vision_text" state
@router_vision.message(StateVisionUrl.vision_text)
async def vision_text(msg: types.Message, l10n: FluentLocalization, state: FSMContext) -> None:
    """
    This function handles the message in the "vision_text" state. It generates a vision from the URL and text using the model stored in the state, and sends this vision as a message.
    If an error occurs during vision generation, it sends a message with the error.
    """
    prompt = msg.text
    data = await state.get_data()
    mesg = await msg.answer(text=l10n.format_value("text_wait"))
    res = await generate_vision_url(model=data["model"], url=data["url"], text=prompt)
    if res.startswith("Error:"):
        await msg.answer(text=res)
    else:
        await mesg.delete()
        await msg.bot.send_message(chat_id=msg.from_user.id, text=res)
