import sounddevice as sd
import numpy as np
import whisper
import queue
import threading
import sys
import os
from googletrans import Translator

# --- Handle Windows encoding (to support Unicode printing) ---
if os.name == "nt":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        os.environ["PYTHONIOENCODING"] = "utf-8"

# Load Whisper model
print("Loading Whisper model...")
model = whisper.load_model("tiny")  # use "tiny" or "base" for faster live performance

# Translator object
translator = Translator()

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 5  # seconds per chunk

# Queue for passing audio data
audio_queue = queue.Queue()

# Step 1: Record audio continuously
def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(indata.copy())

def start_recording():
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        callback=audio_callback,
        blocksize=int(SAMPLE_RATE * CHUNK_DURATION)
    )
    stream.start()
    return stream

# Step 2: Worker thread to transcribe & translate
def transcribe_worker(target_language="fr"):
    print(f"🎤 Live transcription started. Speak into the microphone.")
    print(f"🌍 Translations will appear in: {target_language.upper()}\n(Press Ctrl+C to stop)\n")

    while True:
        audio_chunk = audio_queue.get()
        if audio_chunk is None:
            break

        # Convert audio to the correct format
        audio_data = audio_chunk.flatten().astype(np.float32)

        # Transcribe audio
        result = model.transcribe(audio_data, fp16=False)
        text = result.get("text", "").strip()

        if text:
            print(f"📝 Original: {text}")

            try:
                translated = translator.translate(text, dest=target_language)
                print(f"🌐 Translated ({target_language}): {translated.text}\n")
            except Exception as e:
                print(f"Translation error: {e}")

# Step 3: Start threads
def main():
    stream = start_recording()
    worker = threading.Thread(target=transcribe_worker, daemon=True)
    worker.start()

    try:
        while True:
            sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stream.stop()
        stream.close()
        audio_queue.put(None)

if __name__ == "__main__":
    main()
