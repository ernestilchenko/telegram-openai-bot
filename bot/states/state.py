from aiogram.fsm.state import State, StatesGroup


class StateText(StatesGroup):
    """
    This class represents the state group for text generation. It includes a single state: "text".
    """
    text = State()


class StateImage(StatesGroup):
    """
    This class represents the state group for image generation. It includes a single state: "image".
    """
    image = State()


class StateTextToSpeech(StatesGroup):
    """
    This class represents the state group for text to speech conversion. It includes three states: "text_to_speech",
    "voice", and "text".
    """
    text_to_speech = State()
    voice = State()
    text = State()


class StateSpeechToText(StatesGroup):
    """
    This class represents the state group for speech to text conversion. It includes a single state: "audio_path".
    """
    audio_path = State()


class StateVisionUrl(StatesGroup):
    """
    This class represents the state group for vision from URL. It includes two states: "vision_url" and "vision_text".
    """
    vision_url = State()
    vision_text = State()


class StateVisionPhoto(StatesGroup):
    """
    This class represents the state group for vision from photo. It includes two states: "vision_text" and "vision_photo".
    """
    vision_text = State()
    vision_photo = State()
