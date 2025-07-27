import io
import tkinter as tk
import wave
from tkinter import filedialog, messagebox

from mpmath import mp

from audio_pi_codec_service import (decode_wav_to_string, encode_string_to_wav,
                                    levenshtein_ratio)


class AudioPiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio π Codec GUI")

        self.label = tk.Label(root, text="Число цифр π для кодирования:")
        self.label.pack()

        self.entry = tk.Entry(root)
        self.entry.insert(0, "100")
        self.entry.pack()

        self.encode_button = tk.Button(
            root, text="Кодировать π → WAV", command=self.encode)
        self.encode_button.pack(pady=5)

        self.decode_button = tk.Button(
            root, text="Декодировать WAV", command=self.decode)
        self.decode_button.pack(pady=5)

        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=10)

    def encode(self):
        try:
            n = int(self.entry.get())
            mp.dps = n + 5
            digits = str(mp.pi)[2:2+n]
            wav_bytes = encode_string_to_wav(digits)

            file_path = filedialog.asksaveasfilename(defaultextension=".wav")
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(wav_bytes)
                messagebox.showinfo("Успех", f"Сохранено: {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def decode(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("WAV files", "*.wav")])
        if not file_path:
            return

        with open(file_path, 'rb') as f:
            wav_bytes = f.read()
        decoded = decode_wav_to_string(wav_bytes)

        mp.dps = len(decoded) + 5
        reference = str(mp.pi)[2:2+len(decoded)]
        accuracy = levenshtein_ratio(reference, decoded)

        self.result_label.config(
            text=f"Точность: {accuracy*100:.2f}%\nДекодировано: {decoded[:80]}...")


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioPiApp(root)
    root.mainloop()
