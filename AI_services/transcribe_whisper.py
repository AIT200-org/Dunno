import whisper

model = whisper.load_model("tiny")  # tiny, base, small, medium, large
result = model.transcribe("output.wav")
print("Transcript:")
print(result["text"])
