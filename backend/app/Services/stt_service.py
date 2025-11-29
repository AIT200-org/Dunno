class SpeechToTextService:
	def __init__(self, model_name: str = None):
		# Lazy-load Whisper model to avoid heavy imports at module import time
		from utils.whisper_loader import load_whisper_model
		self.model = load_whisper_model(model_name or "base")

	def transcribe(self, audio_path: str) -> dict:
		result = self.model.transcribe(audio_path)
		return {"text": result.get("text", ""), "segments": result.get("segments", []), "duration": result.get("duration")}

