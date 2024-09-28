import openai
from aiogram import Router, types, F, flags
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from bot.config import client
from ...states.state import StateImage

router_image = Router()


async def generate_image(prompt: str, model: str) -> str:
    """
    This function generates an image based on the provided prompt and model.

    Parameters:
    prompt (str): The prompt to be used for image generation.
    model (str): The model to be used for image generation. It can be "dall-e-3" or "dall-e-2".

    Returns:
    str: The URL of the generated image. If an error occurs during image generation, it returns a string starting with "Error:" followed by the error message.
    """
    try:
        # Generate the image using the OpenAI API
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        # Return the URL of the generated image
        return response.data[0].url
    except openai.OpenAIError as e:
        # If an error occurs, return the error message
        return f"Error: {str(e)}"


@router_image.callback_query(F.data == "image")
async def image(call: types.CallbackQuery, l10n: FluentLocalization):
    buttons_image = [
        [types.InlineKeyboardButton(text="dall-e-3", callback_data="dall-e-3")],
        [types.InlineKeyboardButton(text="dall-e-2", callback_data="dall-e-2")],
        [types.InlineKeyboardButton(text="🔙Back", callback_data="back")]
    ]
    keyboard_image = types.InlineKeyboardMarkup(inline_keyboard=buttons_image)
    await call.message.edit_text(text=l10n.format_value("text_image"), reply_markup=keyboard_image)


@router_image.callback_query(F.data.startswith("dall"))
async def dall(call: types.CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    await call.message.bot.send_message(chat_id=call.message.chat.id, text=l10n.format_value("text_dall"))
    await state.update_data(model=call.data)
    await state.set_state(StateImage.image)


@router_image.message(StateImage.image)
@flags.chat_action("upload_photo")
async def image(msg: types.Message, state: FSMContext, l10n: FluentLocalization) -> None:
    """
    This function handles the message in the "image" state. It generates an image based on the message text and the model stored in the state,
    and sends this image as a photo. If an error occurs during image generation, it sends a message with the error.
    """
    prompt = msg.text
    data = await state.get_data()
    mesg = await msg.answer(text=l10n.format_value("text_wait"))
    res = await generate_image(prompt=prompt, model=data["model"])
    if res.startswith("Error:"):
        await msg.answer(text=res)
    else:
        await mesg.delete()
        await msg.bot.send_photo(chat_id=msg.from_user.id, photo=res)
