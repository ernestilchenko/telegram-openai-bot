from aiogram import Router, types
from aiogram.filters import CommandStart
from fluent.runtime import FluentLocalization

router_start = Router()


@router_start.message(CommandStart())
async def start(msg: types.Message, l10n: FluentLocalization):
    buttons_start = [
        [types.InlineKeyboardButton(text=l10n.format_value("text"), callback_data="text"),
         types.InlineKeyboardButton(text=l10n.format_value("image"), callback_data="image")],
        [types.InlineKeyboardButton(text=l10n.format_value("variation"), callback_data="variation"),
         types.InlineKeyboardButton(text=l10n.format_value("vision"), callback_data="vision")],
        [types.InlineKeyboardButton(text=l10n.format_value("text_to_speech"), callback_data="text_to_speech"),
         types.InlineKeyboardButton(text=l10n.format_value("speech_to_text"), callback_data="speech_to_text")],
        [types.InlineKeyboardButton(text=l10n.format_value("help"), url="https://t.me/ernestilchenko")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons_start)
    await msg.answer(text=l10n.format_value("cmd-start", args={"name": msg.from_user.full_name}), reply_markup=keyboard)
