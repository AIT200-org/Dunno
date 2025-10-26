import sounddevice as sd
import numpy as np
import whisper
import queue
import threading
import sys

# Whisper model (base is a good starting point for real-time speed)
print("Loading Whisper model...")
model = whisper.load_model("base")  # you can also use "small" or "tiny" for faster

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 5  # seconds per chunk (lower for faster feedback, but too low can hurt accuracy)

# A thread-safe queue to collect audio chunks
audio_queue = queue.Queue()

# ====== Step 1: Continuously record audio and push to queue ======
def audio_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # convert audio to float32 numpy array
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

# ====== Step 2: Worker thread: take chunks and transcribe ======
def transcribe_worker():
    print("Live transcription started. Speak into the microphone\n(Press Ctrl+C to stop)\n")
    while True:
        audio_chunk = audio_queue.get()
        if audio_chunk is None:
            break

        # Flatten and convert to float32
        audio_data = audio_chunk.flatten().astype(np.float32)

        # Transcribe this chunk
        result = model.transcribe(audio_data, fp16=False)
        text = result.get("text", "").strip()

        if text:
            print(f">>> {text}")

# ====== Step 3: Run threads ======
def main():
    stream = start_recording()
    worker = threading.Thread(target=transcribe_worker, daemon=True)
    worker.start()

    try:
        while True:
            sd.sleep(1000)  # keep main thread alive
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stream.stop()
        stream.close()
        audio_queue.put(None)

if __name__ == "__main__":
    main()
