import io
import wave

import numpy as np
from mpmath import mp

from audio_pi_codec_service import (decode_wav_to_string, encode_string_to_wav,
                                    levenshtein_ratio)

# Настройка точности Pi
mp.dps = 1000
pi_digits = str(mp.pi)[2:]  # убираем "3."

# Сколько цифр проверяем (не больше 200 — ограничение WAV)
N = 100000000000
message = pi_digits[:N]

print(f"Тестируем {N} цифр числа π")

# Генерация WAV в памяти
wav_bytes = encode_string_to_wav(message)

# Декодирование из WAV
decoded = decode_wav_to_string(wav_bytes)

# Расчёт точности
accuracy = levenshtein_ratio(message[:len(decoded)], decoded)

print("Оригинал:", message[:80] + "...")
print("Декодировано:", decoded[:80] + "...")
print()
print(f"Точность восстановления: {accuracy * 100:.2f}%")
