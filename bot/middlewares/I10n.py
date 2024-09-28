from typing import Any, Awaitable, Callable, Dict, Final

from aiogram import BaseMiddleware
from aiogram.enums import ChatType
from aiogram.types import TelegramObject, User, Update

from bot.utils.fluent_helper import FluentDispenser


def is_pm(event: Update) -> bool:
    """
    This function checks if the event is a private message.

    Args:
        event (Update): The event object to check.

    Returns:
        bool: True if the event is a private message, False otherwise.
    """
    return \
            (event.message and event.message.chat.type == ChatType.PRIVATE) or \
            (event.inline_query and event.inline_query.chat_type == ChatType.SENDER)


class L10nMiddleware(BaseMiddleware):
    """
    This class is a middleware for localization.

    It inherits from the BaseMiddleware class provided by aiogram.

    The __call__ method is overridden to provide the custom middleware logic.
    """
    middleware_key: Final[str] = "l10n"

    def __init__(self, dispenser: FluentDispenser):
        """
        This method initializes the L10nMiddleware class.

        Args:
            dispenser (FluentDispenser): The FluentDispenser instance to use for localization.
        """
        self.dispenser = dispenser

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        This method is an asynchronous method that is called when the middleware is applied to an event.

        It sets the localization for the event based on the user's language code.

        Args:
            handler (Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]]): The handler to call after the middleware is applied.
            event (TelegramObject): The event object that the middleware is applied to.
            data (Dict[str, Any]): The data associated with the event.

        Returns:
            Any: The result of the handler.
        """
        event: Update
        if is_pm(event):
            user: User = data["event_from_user"]
            data[self.middleware_key] = self.dispenser.get_language(user.language_code)
        else:
            data[self.middleware_key] = self.dispenser.default_locale

        return await handler(event, data)
