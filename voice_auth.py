import numpy as np
import pickle
import sounddevice as sd
from scipy.io.wavfile import write
from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import tempfile, os

SAMPLE_RATE = 16000
SIMILARITY_THRESHOLD = 0.75

encoder = VoiceEncoder()

# Load boss embedding at startup
with open("owner_voice.pkl", "rb") as f:
    BOSS_EMBEDDING = pickle.load(f)


def record_snippet(duration=3) -> np.ndarray:
    """Record a short audio snippet and return as numpy array."""
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    return audio


def get_similarity(audio: np.ndarray) -> float:
    """Compare audio snippet against boss voice. Returns cosine similarity 0-1."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name
    try:
        write(tmp_path, SAMPLE_RATE, (audio * 32767).astype(np.int16))
        wav = preprocess_wav(Path(tmp_path))
        embedding = encoder.embed_utterance(wav)
        similarity = float(np.dot(BOSS_EMBEDDING, embedding) /
                          (np.linalg.norm(BOSS_EMBEDDING) * np.linalg.norm(embedding)))
        return similarity
    finally:
        os.unlink(tmp_path)


def is_boss(audio: np.ndarray) -> bool:
    similarity = get_similarity(audio)
    print(f"[VoiceAuth] Similarity score: {similarity:.3f}")
    return similarity >= SIMILARITY_THRESHOLD