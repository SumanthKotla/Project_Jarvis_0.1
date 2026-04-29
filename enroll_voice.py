import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import pickle

SAMPLE_RATE = 16000
DURATION = 10

print("Recording your voice for 10 seconds... speak naturally.")
audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
sd.wait()
print("Done recording.")

wav_path = Path("boss_sample.wav")
write(str(wav_path), SAMPLE_RATE, (audio * 32767).astype(np.int16))

encoder = VoiceEncoder()
wav = preprocess_wav(wav_path)
embedding = encoder.embed_utterance(wav)

with open("boss_voice.pkl", "wb") as f:
    pickle.dump(embedding, f)

print("✅ Voice enrolled and saved to boss_voice.pkl")
wav_path.unlink()
