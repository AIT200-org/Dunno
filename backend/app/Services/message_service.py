from typing import Iterable, Optional
from sqlalchemy.orm import Session
from models import Message, Translation, SpeechData
from .translation_service import TranslationService
from .stt_service import SpeechToTextService


class MessageService:
    def __init__(self, translation: Optional[TranslationService] = None, stt: Optional[SpeechToTextService] = None):
        self.translation = translation or TranslationService()
        self.stt = stt or SpeechToTextService()

    def create_text_message(self, db: Session, owner_id: int, group_id: Optional[int], text: str, target_langs: Iterable[str]):
        """Create a text message, detect language, produce translations and store them.

        Returns the created Message and a dict of target_lang -> translated_text.
        """
        # detect source language
        source_lang = self.translation.detect_language(text)

        # create message
        msg = Message(owner_id=owner_id, group_id=group_id, content=text, language=source_lang)
        db.add(msg)
        db.commit()
        db.refresh(msg)

        translations = {}
        for lang in target_langs:
            if lang == source_lang:
                translations[lang] = text
                continue

            translated = self.translation.translate(text, lang)
            translations[lang] = translated

            tr = Translation(user_id=owner_id, message_id=msg.id, source_lang=source_lang, target_lang=lang, original_text=text, translated_text=translated)
            db.add(tr)

        db.commit()

        return {"message": msg, "source_lang": source_lang, "translations": translations}

    def create_audio_message(self, db: Session, owner_id: int, group_id: Optional[int], audio_path: str, target_langs: Iterable[str]):
        # transcribe audio
        transcript = self.stt.transcribe(audio_path)
        text = transcript.get("text", "")

        # create message from transcription
        result = self.create_text_message(db, owner_id, group_id, text, target_langs)

        # record speech metadata
        msg = result["message"]
        sd = SpeechData(user_id=owner_id, message_id=msg.id, audio_path=audio_path, duration=transcript.get("duration"))
        db.add(sd)
        db.commit()

        return result
