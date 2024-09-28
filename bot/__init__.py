from aiogram import Router

from .handlers.api.image import router_image
from .handlers.api.speech_to_text import router_speech_to_text
from .handlers.api.text import router_text
from .handlers.api.text_to_speech import router_text_to_speech
from .handlers.api.vision import router_vision
from .handlers.start import router_start


def setup_routers() -> Router:
    router = Router()
    router.include_router(router=router_start)
    router.include_router(router=router_text)
    router.include_router(router=router_image)
    router.include_router(router=router_text_to_speech)
    router.include_router(router=router_speech_to_text)
    router.include_router(router=router_vision)
    return router
