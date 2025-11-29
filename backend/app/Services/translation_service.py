from typing import List


class TranslationService:
	"""Translation service that supports local MarianMT or a configured LLM.

	The loader returns either:
	  - a dict with keys 'tokenizer' and 'model' for local MarianMT
	  - an LLM object (LangChain ChatOpenAI) for remote translation
	"""

	def __init__(self):
		# Lazy import to avoid importing heavy translator libs at module import time
		from utils.translator_loader import load_translator
		self.translator = load_translator()

	def translate(self, text: str, target_lang: str) -> str:
		# Local MarianMT path
		if isinstance(self.translator, dict) and "model" in self.translator:
			tokenizer = self.translator["tokenizer"]
			model = self.translator["model"]
			# prepare inputs for MarianMT
			inputs = tokenizer.prepare_seq2seq_batch([text], return_tensors="pt")
			translated = model.generate(**inputs)
			out = tokenizer.batch_decode(translated, skip_special_tokens=True)
			return out[0]

		# LLM path (LangChain ChatOpenAI or similar)
		llm = self.translator
		prompt = f"Translate the following text to {target_lang}. Only return the translation.\n\n{text}"
		if hasattr(llm, "generate"):
			res = llm.generate([prompt])
			try:
				return res.generations[0][0].text
			except Exception:
				return str(res)

		if hasattr(llm, "__call__"):
			try:
				return llm(prompt)
			except Exception:
				pass

		raise RuntimeError("Configured translator is not compatible with TranslationService. Use local MarianMT or a LangChain LLM with a sync API.")

	def detect_language(self, text: str) -> str:
		if isinstance(self.translator, dict):
			return "en"

		llm = self.translator
		prompt = "Detect the language of this text. Return only ISO code.\n\n" + text
		if hasattr(llm, "generate"):
			res = llm.generate([prompt])
			try:
				return res.generations[0][0].text.strip()
			except Exception:
				return "en"

		if hasattr(llm, "__call__"):
			try:
				out = llm(prompt)
				return out.strip()
			except Exception:
				return "en"

		return "en"
