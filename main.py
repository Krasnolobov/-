import os
import sys
import webbrowser

MENU = """
Выберите режим запуска:

1. Веб-сервис (FastAPI)
2. Автотест точности π → WAV → π
3. GUI (Tkinter-интерфейс)
0. Выход
"""

while True:
    print(MENU)
    choice = input("Введите номер: ").strip()

    if choice == "1":
        print("Запуск веб-сервиса на http://127.0.0.1:8000")
        webbrowser.open("http://127.0.0.1:8000/docs")
        os.system("uvicorn audio_pi_codec_service:app --reload")
    elif choice == "2":
        os.system(f"python test_accuracy_pi.py")
    elif choice == "3":
        os.system(f"python gui_audio_pi_codec.py")
    elif choice == "0":
        print("Выход.")
        sys.exit(0)
    else:
        print("Неверный ввод. Попробуйте снова.")
