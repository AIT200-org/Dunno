import pyaudio
import wave

# Settings
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1              # mono
RATE = 16000              # 16 kHz sample rate
CHUNK = 1024              # number of frames per buffer
RECORD_SECONDS = 5        # record duration
OUTPUT_FILENAME = "output.wav"

# Initialize
audio = pyaudio.PyAudio()

# Start Recording
print("Recording...")
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
frames = []

for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Finished recording.")

# Stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

# Save the file
wf = wave.open(OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(audio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print(f"Saved as {OUTPUT_FILENAME}")
