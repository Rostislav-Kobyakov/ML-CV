import speech_recognition as sr
import time
from datetime import datetime


class Recognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = Microfon()

    def recognize_speech(self):
        audio = self.microphone.get_audio()
        if audio is None:
            return None
        try:
            text = self.recognizer.recognize_google(audio, language="ru-RU")
            print(f"Распознанная команда: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Не удалось распознать речь")
            return None
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")
            return None


class Microfon:
    def __init__(self):
        self.mic = sr.Microphone()
        self.recognizer = sr.Recognizer()
        # Однократная настройка шумоподавления при инициализации
        with self.mic as source:
            print("Настройка шумоподавления (это займёт пару секунд)...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Настройка завершена")

    def get_audio(self):
        with self.mic as source:
            print("Слушаю...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                return audio
            except sr.WaitTimeoutError:
                print("Тайм-аут: не услышал голос")
                return None


class VoiceAssistant:
    def __init__(self):
        self.recognizer = Recognizer()
        self.notes_file = "notes.txt"

    def create_note(self, note_text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.notes_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {note_text}\n")
        print(f"Заметка сохранена: {note_text}")

    def custom_command(self):
        print("Персональная команда выполнена: Текущая дата и время")
        print(f"Сегодня: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def process_command(self, command):
        if command:
            if "заметка" in command:
                note_text = command.replace("заметка", "").strip()
                if note_text:
                    self.create_note(note_text)
                else:
                    print("Пожалуйста, укажите текст заметки")
            elif "персональная команда" in command:
                self.custom_command()
            elif "выход" in command:
                print("Завершение работы помощника")
                return False
            else:
                print("Команда не распознана")
        return True

    def run(self):
        print("Голосовой помощник запущен. Доступные команды:")
        print("- 'Заметка [текст]' - создать заметку")
        print("- 'Персональная команда' - показать текущую дату и время")
        print("- 'Выход' - завершить работу")

        while True:
            command = self.recognizer.recognize_speech()
            if not self.process_command(command):
                break
            time.sleep(1)


if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.run()