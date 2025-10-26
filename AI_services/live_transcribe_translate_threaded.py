import sounddevice as sd
import numpy as np
import whisper
import queue
import threading
import sys
import os
from googletrans import Translator

# Fix Windows terminal Unicode printing
if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        os.environ["PYTHONIOENCODING"] = "utf-8"

# Load Whisper model and Translator
print("⏳ Loading Whisper model...")
model = whisper.load_model("tiny")  # use "tiny" or "base" for speed
translator = Translator()

# Settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 5  # seconds of audio per chunk

# Queues
audio_queue = queue.Queue()
text_queue = queue.Queue()

# Event to signal shutdown
stop_event = threading.Event()


# 🎤 Audio callback
def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(indata.copy())


# 🧠 Transcription worker
def transcribe_worker():
    print("🎤 Transcription started. Speak into the microphone.")
    while not stop_event.is_set():
        audio_chunk = audio_queue.get()
        if audio_chunk is None:
            break

        audio_data = audio_chunk.flatten().astype(np.float32)

        # Transcribe the chunk
        result = model.transcribe(audio_data, fp16=False)
        text = result.get("text", "").strip()
        if text:
            print(f"📝 Original: {text}")
            text_queue.put(text)  # send text to translation thread


# 🌍 Translation worker
def translate_worker(target_language="fr"):
    print(f"🌍 Translation thread started (→ {target_language.upper()})\n")
    while not stop_event.is_set():
        try:
            text = text_queue.get(timeout=1)
        except queue.Empty:
            continue

        if text is None:
            break

        try:
            translated = translator.translate(text, dest=target_language)
            print(f"🌐 Translated ({target_language}): {translated.text}\n")
        except Exception as e:
            print(f"❌ Translation error: {e}")


def main():
    # Start recording stream
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        callback=audio_callback,
        blocksize=int(SAMPLE_RATE * CHUNK_DURATION)
    )
    stream.start()

    # Start threads
    t1 = threading.Thread(target=transcribe_worker, daemon=True)
    t2 = threading.Thread(target=translate_worker, daemon=True)
    t1.start()
    t2.start()

    try:
        while True:
            sd.sleep(1000)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    finally:
        stop_event.set()
        stream.stop()
        stream.close()
        audio_queue.put(None)
        text_queue.put(None)
        t1.join()
        t2.join()
        print("✅ All threads stopped cleanly.")


if __name__ == "__main__":
    main()
