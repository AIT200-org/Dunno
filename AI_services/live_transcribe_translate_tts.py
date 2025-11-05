"""
live_transcribe_translate_tts.py
Real-time capture -> Whisper transcribe -> translate -> speak (TTS)
Uses 3 threads + queues:
 - audio_queue  : mic -> transcribe_worker
 - text_queue   : transcribe_worker -> translate_worker
 - tts_queue    : translate_worker -> tts_worker
"""

import os
import sys
import queue
import threading
import sounddevice as sd
import numpy as np
import whisper
from googletrans import Translator
import pyttsx3
import time
import traceback

# --- Ensure UTF-8 output on Windows consoles ---
if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        os.environ["PYTHONIOENCODING"] = "utf-8"

# --- Settings ---
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 3          # seconds per chunk (3s gives faster feedback)
MODEL_NAME = "tiny"         # tiny or base recommended for live use
TARGET_LANGUAGE = "fr"      # translation target (change as needed, e.g., "es", "de", "hi")

# --- Queues and control event ---
audio_queue = queue.Queue()
text_queue = queue.Queue()
tts_queue = queue.Queue()
stop_event = threading.Event()

# --- Load models / services ---
print("⏳ Loading Whisper model (this may take a moment)...")
model = whisper.load_model(MODEL_NAME)
translator = Translator()

# --- Initialize TTS engine (pyttsx3) ---
tts_engine = pyttsx3.init()
# Optional: tune voice properties (rate, volume). We'll set a reasonable speaking rate:
rate = tts_engine.getProperty("rate")
tts_engine.setProperty("rate", int(rate * 0.95))  # slightly slower than default
# Optional: choose a voice matching a language (best-effort)
voices = tts_engine.getProperty("voices")
# Example: try to pick a voice whose name or languages hint at the target language
preferred_voice = None
for v in voices:
    name_lower = (v.name or "").lower()
    langs = getattr(v, "languages", None) or []
    lang_hint = ",".join([str(x).lower() for x in langs])
    if TARGET_LANGUAGE in name_lower or TARGET_LANGUAGE in lang_hint:
        preferred_voice = v.id
        break
if preferred_voice:
    tts_engine.setProperty("voice", preferred_voice)

# --- Audio callback (producer) ---
def audio_callback(indata, frames, time_info, status):
    if status:
        # nonfatal status messages (overruns etc.)
        print("Audio status:", status, file=sys.stderr)
    # copy to ensure the buffer isn't reused underneath us
    audio_queue.put(indata.copy())

# --- Transcription worker (consumer -> produce text) ---
def transcribe_worker():
    print("🎤 Transcription thread started.")
    while not stop_event.is_set():
        try:
            audio_chunk = audio_queue.get(timeout=1)
        except queue.Empty:
            continue
        if audio_chunk is None:
            break

        # Convert to 1-D float32 array (Whisper accepts numpy arrays)
        try:
            audio_data = audio_chunk.flatten().astype(np.float32)
            # Whisper supports passing numpy arrays directly
            result = model.transcribe(audio_data, fp16=False)
            text = result.get("text", "").strip()
            if text:
                print(f"📝 Original: {text}")
                text_queue.put(text)
        except Exception as e:
            print("Error in transcribe_worker:", e)
            traceback.print_exc()

# --- Translation worker (consume text -> produce translated text for TTS) ---
def translate_worker(target_language=TARGET_LANGUAGE):
    print(f"🌍 Translation thread started -> {target_language.upper()}")
    while not stop_event.is_set():
        try:
            text = text_queue.get(timeout=1)
        except queue.Empty:
            continue
        if text is None:
            break

        try:
            translated = translator.translate(text, dest=target_language)
            translated_text = translated.text
            print(f"🌐 Translated ({target_language}): {translated_text}\n")
            # Send translated text to TTS queue
            tts_queue.put(translated_text)
        except Exception as e:
            print("Translation error:", e)
            traceback.print_exc()

# --- TTS worker (speak translated text) ---
def tts_worker():
    print("🔊 TTS thread started.")
    # Note: pyttsx3's engine is not thread-safe across multiple processes,
    # but it's fine to drive it from a single dedicated thread.
    # We will call engine.say() then runAndWait() for each phrase.
    while not stop_event.is_set():
        try:
            text = tts_queue.get(timeout=1)
        except queue.Empty:
            continue
        if text is None:
            break
        try:
            # speak the text
            tts_engine.say(text)
            tts_engine.runAndWait()  # blocks inside this thread until speech finishes
        except Exception as e:
            print("TTS error:", e)
            traceback.print_exc()

# --- Main: start stream and threads ---
def main():
    # Open input stream with blocksize equal to chunk duration
    blocksize = int(SAMPLE_RATE * CHUNK_DURATION)
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        callback=audio_callback,
        blocksize=blocksize
    )

    # Start threads
    t_trans = threading.Thread(target=transcribe_worker, daemon=True)
    t_trans.start()
    t_translator = threading.Thread(target=translate_worker, daemon=True)
    t_translator.start()
    t_tts = threading.Thread(target=tts_worker, daemon=True)
    t_tts.start()

    print("▶️ Starting audio stream. Press Ctrl+C to stop.")
    try:
        with stream:
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\n🛑 Stopping (Ctrl+C pressed)...")
    finally:
        stop_event.set()
        # send sentinels so threads exit promptly
        audio_queue.put(None)
        text_queue.put(None)
        tts_queue.put(None)
        t_trans.join()
        t_translator.join()
        t_tts.join()
        # optionally stop tts_engine
        try:
            tts_engine.stop()
        except Exception:
            pass
        print("✅ All stopped. Goodbye.")

if __name__ == "__main__":
    main()
