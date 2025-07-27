import io
import wave
from difflib import SequenceMatcher
from typing import List

import numpy as np
from fastapi import FastAPI, Form, UploadFile
from fastapi.responses import StreamingResponse
from mpmath import mp
from scipy.fftpack import fft

# Создаём FastAPI приложение
app = FastAPI()

# === Настройки ===
RATE = 44100  # 44.1 kHz
DURATION = 0.01  # Длительность одного символа в секундах (10 мс)
GAP = 0.0       # Зазор между символами (тишина)
REPEATS = 1      # Повторов одного символа
AMPLITUDE = 16000  # Амплитуда сигнала

DIGIT_FREQUENCIES = {
    '0': 1000,
    '1': 1100,
    '2': 1200,
    '3': 1300,
    '4': 1400,
    '5': 1500,
    '6': 1600,
    '7': 1700,
    '8': 1800,
    '9': 1900
}
REVERSE_FREQ_MAP = {v: k for k, v in DIGIT_FREQUENCIES.items()}
FREQ_TOLERANCE = 30  # Гц


# === Генерация WAV ===
def encode_string_to_wav(text: str) -> bytes:
    samples = []
    for char in text:
        freq = DIGIT_FREQUENCIES.get(char, None)
        if freq is None:
            continue
        t = np.linspace(0, DURATION, int(RATE * DURATION), False)
        wave_data = AMPLITUDE * np.sin(2 * np.pi * freq * t)
        silence = np.zeros(int(RATE * GAP))
        for _ in range(REPEATS):
            samples.extend(wave_data)
            samples.extend(silence)

    samples = np.array(samples, dtype=np.int16)
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(RATE)
        wf.writeframes(samples.tobytes())

    buffer.seek(0)
    return buffer.read()


# === Декодирование WAV ===
def decode_wav_to_string(wav_bytes: bytes) -> str:
    with wave.open(io.BytesIO(wav_bytes), 'rb') as wf:
        n_frames = wf.getnframes()
        frames = wf.readframes(n_frames)
        samples = np.frombuffer(frames, dtype=np.int16)

    step = int(RATE * (DURATION + GAP))
    decoded = []
    for i in range(0, len(samples), step):
        segment = samples[i:i + int(RATE * DURATION)]
        if len(segment) < int(RATE * DURATION):
            continue
        segment = segment - np.mean(segment)
        segment *= np.hanning(len(segment))  # сглаживание окна Ханна
        spectrum = np.abs(fft(segment))[:len(segment) // 2]
        freqs = np.fft.fftfreq(len(segment), 1 / RATE)[:len(segment) // 2]
        peak_freq = freqs[np.argmax(spectrum)]
        match = None
        for base_freq, digit in REVERSE_FREQ_MAP.items():
            if abs(peak_freq - base_freq) <= FREQ_TOLERANCE:
                match = digit
                break
        if match:
            decoded.append(match)

    # Сглаживание повторов: берём каждый REPEATS-й символ (или медиану блоков)
    final = []
    for i in range(0, len(decoded), REPEATS):
        block = decoded[i:i+REPEATS]
        if not block:
            continue
        final.append(max(set(block), key=block.count))

    return ''.join(final)


# === API ===
@app.post("/encode")
def encode_pi(n_digits: int = Form(...)):
    mp.dps = n_digits + 5
    pi_digits = str(mp.pi)[2:2+n_digits]
    max_digits = int((RATE * 10) // ((DURATION + GAP) * RATE * REPEATS))
    truncated = pi_digits[:max_digits]
    wav_bytes = encode_string_to_wav(truncated)
    return StreamingResponse(io.BytesIO(wav_bytes), media_type="audio/wav", headers={
        "Content-Disposition": "attachment; filename=pi.wav"
    })


@app.post("/decode")
def decode_pi(file: UploadFile):
    wav_bytes = file.file.read()
    decoded = decode_wav_to_string(wav_bytes)
    mp.dps = len(decoded) + 5
    reference = str(mp.pi)[2:2+len(decoded)]
    accuracy = levenshtein_ratio(reference, decoded)
    return {"decoded": decoded, "reference": reference, "accuracy": round(accuracy * 100, 2)}


# === Тест Левенштейна (на точность) ===
def levenshtein_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()
