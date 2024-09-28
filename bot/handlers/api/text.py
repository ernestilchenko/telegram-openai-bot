import openai
from aiogram import types, Router, F, flags
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from ...config import client
from ...states.state import StateText

router_text = Router()


async def generate_text(prompt: str, model: str) -> str:
    """
    This function generates text based on the provided prompt and model.

    Parameters:
    prompt (str): The prompt to be used for text generation.
    model (str): The model to be used for text generation. It can be "gpt-4" or "gpt-3.5-turbo".

    Returns:
    str: The generated text. If an error occurs during text generation, it returns a string starting with "Error:" followed by the error message.
    """
    try:
        # Custom system prompt with instructions
        system_prompt = """
        You must follow the rules before answering:
        - I have no fingers and the truncate trauma.
        - I need you to return the entire code template or answer. DON’T use placeholders.
        - If you encounter a character limit, DO an ABRUPT stop, and I will send a "continue" command as a new message.
        - DO follow "Answering rules" without exception.
        - DO write your answers for a well-educated audience.
        - You will be PENALIZED for wrong answers.

        Do follow the rules in strict order:
        1. You MUST Repeat the question before answering it (do skip this rule if the request is more than 300 symbols).
        2. Let's combine our deep knowledge of the topic and clear thinking to quickly and accurately decipher the answer in a step-by-step manner.
        3. I'm going to tip $100,000 for a better solution.
        4. The answer is very important to my career.
        5. Answer the question in a natural, human-like manner.
        """

        # Generate the text using the OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]
        )

        # Return the generated text
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        # If an error occurs, return the error message
        return f"Error: {str(e)}"


@router_text.callback_query(F.data == "text")
async def text(call: types.CallbackQuery, l10n: FluentLocalization):
    # Inline keyboard buttons for selecting the text generation model
    buttons_text = [
        [types.InlineKeyboardButton(text="🧠 GPT-4", callback_data="gpt-4")],
        [types.InlineKeyboardButton(text="⚡ GPT-4o", callback_data="gpt-4o")],
        [types.InlineKeyboardButton(text="🔙 Back", callback_data="back")]
    ]

    # Inline keyboard markup for the text generation model selection
    keyboard_text = types.InlineKeyboardMarkup(inline_keyboard=buttons_text)
    await call.message.edit_text(text=l10n.format_value("text_text"), reply_markup=keyboard_text)


@router_text.callback_query(F.data.startswith("gpt-"))
async def gpt(call: types.CallbackQuery, state: FSMContext, l10n: FluentLocalization):
    await call.message.bot.send_message(chat_id=call.message.chat.id,
                                        text=l10n.format_value(msg_id=f"text_{call.data}"))
    await state.update_data(model=call.data)
    await state.set_state(StateText.text)


@router_text.message(StateText.text)
@flags.chat_action("typing")
async def text(msg: types.Message, l10n: FluentLocalization, state: FSMContext):
    prompt = msg.text
    data = await state.get_data()
    mesg = await msg.answer(text=l10n.format_value(msg_id="text_wait"))
    res = await generate_text(prompt=prompt, model=data["model"])
    if res.startswith("Error:"):
        await msg.answer(text=res)
    else:
        await mesg.delete()
        await msg.bot.send_message(chat_id=msg.from_user.id, text=res)
