import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
# from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot import setup_routers
from bot.config import TOKEN_TELEGRAM
from bot.middlewares.I10n import L10nMiddleware
from bot.utils.fluent_helper import FluentDispenser


async def main():
    """
    This is the main function that initializes the bot, sets up the routers, and starts polling for updates.

    It is asynchronous because it involves IO operations (communicating with the Telegram API).

    Returns:
        None
    """
    # Initialize the bot with the Telegram token and set the parse mode to HTML
    bot = Bot(token=TOKEN_TELEGRAM)

    # Initialize the dispatcher with memory storage
    dp = Dispatcher(storage=MemoryStorage())

    # Set up the routers for handling different types of updates
    router = setup_routers()
    dp.include_routers(router)

    # Initialize the localization middleware
    dispenser = FluentDispenser(
        locales_dir=Path(__file__).parent.joinpath("bot/locales"),
        default_language="en"
    )
    dp.update.middleware(L10nMiddleware(dispenser))

    # Delete any existing webhooks and start polling for updates
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    """
    This is the entry point of the script.

    It sets up logging and starts the main function.
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Start the main function
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
