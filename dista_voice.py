import sys
import threading
from PyQt6.QtCore import QThread, pyqtSignal

class TTSWorker(QThread):
    """
    Background Thread for pyttsx3 Text-to-Speech
    Ensures zero UI blocking while Dista is speaking.
    """
    started_speaking = pyqtSignal()
    finished_speaking = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def run(self):
        self.started_speaking.emit()
        try:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except Exception:
                pass

            import pyttsx3
            engine = pyttsx3.init()
            
            # Configure voice rate and volume
            engine.setProperty('rate', 165)
            engine.setProperty('volume', 0.95)
            
            # Try to select a smooth voice
            voices = engine.getProperty('voices')
            if voices:
                for v in voices:
                    if "david" in v.name.lower() or "zira" in v.name.lower() or "english" in v.name.lower():
                        engine.setProperty('voice', v.id)
                        break

            engine.say(self.text)
            engine.runAndWait()
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except Exception:
                pass
            self.finished_speaking.emit()


class STTWorker(QThread):
    """
    Background Thread for Speech-to-Text (Microphone input)
    Uses speech_recognition (offline Sphinx or Web Speech) with graceful fallbacks.
    """
    recognized_text = pyqtSignal(str)
    listening_started = pyqtSignal()
    listening_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def run(self):
        self.listening_started.emit()
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 300
            recognizer.pause_threshold = 0.8

            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

            # Recognize using Google Web Speech (free online) or Sphinx (offline fallback)
            try:
                text = recognizer.recognize_google(audio)
            except Exception:
                text = recognizer.recognize_sphinx(audio)

            if text:
                self.recognized_text.emit(text)
            else:
                self.error_occurred.emit("No clear speech detected.")

        except ImportError:
            self.error_occurred.emit("SpeechRecognition or PyAudio not installed. Use text input below.")
        except Exception as e:
            self.error_occurred.emit(f"Microphone error: {str(e)}")
        finally:
            self.listening_finished.emit()
