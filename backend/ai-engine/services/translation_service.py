import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.en_translator = GoogleTranslator(source='auto', target='en')
        self.kn_translator = GoogleTranslator(source='en', target='kn')

    def translate_to_english(self, text: str) -> tuple[str, str]:
        """Translates input text to English and detects source language."""
        if not text or len(text.strip()) == 0:
            return text, 'en'
            
        try:
            # We assume if there are Kannada characters, it's Kannada. 
            # Otherwise we let the translator handle it.
            is_kannada = any('\u0C80' <= char <= '\u0CFF' for char in text)
            
            if is_kannada:
                translated = self.en_translator.translate(text)
                return translated, 'kn'
            
            return text, 'en'
        except Exception as e:
            logger.warning(f"Translation to English failed: {e}")
            return text, 'en'

    def translate_from_english(self, text: str, target_lang: str) -> str:
        """Translates english text to target language."""
        if target_lang == 'en' or not text:
            return text
            
        try:
            if target_lang == 'kn':
                return self.kn_translator.translate(text)
            return text
        except Exception as e:
            logger.warning(f"Translation to {target_lang} failed: {e}")
            return text
