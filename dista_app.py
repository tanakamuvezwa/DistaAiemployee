import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget, QFrame,
    QGridLayout, QListWidget, QListWidgetItem, QStackedWidget, QInputDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont

from dista_avatar import DistaAvatar
from dista_waveform import DistaWaveform
from dista_voice import TTSWorker, STTWorker
from dista_brain import DistaBrain
from dista_tools import EmailTool, DocsTool, MessagesTool


class DistaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DISTA AI")
        self.resize(440, 820)
        self.setMinimumSize(380, 700)

        # Core Engine Setup
        self.brain = DistaBrain()
        self.tts_worker = None
        self.stt_worker = None

        # Load QSS Theme
        qss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dista_style.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

        self._init_ui()

        # Initial Speech Greeting
        QTimer.singleShot(400, self._speak_greeting)

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(12)

        # ── 1. HEADER BAR ──────────────────────────────────────────────
        header_layout = QHBoxLayout()
        
        btn_menu = QPushButton("≡")
        btn_menu.setFixedSize(32, 32)
        btn_menu.setStyleSheet("border:none; font-size:20px; color:#8C94A8; font-weight:bold;")
        
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(4)
        lbl_dista = QLabel("DISTA")
        lbl_dista.setObjectName("header_brand")
        lbl_ai = QLabel("AI")
        lbl_ai.setObjectName("header_brand_accent")
        brand_layout.addWidget(lbl_dista)
        brand_layout.addWidget(lbl_ai)
        brand_layout.addStretch()

        btn_key = QPushButton("🔑")
        btn_key.setFixedSize(32, 32)
        btn_key.setStyleSheet("background:#1A1C28; border:1px solid #FF6B00; border-radius:16px; font-size:14px; color:#FF6B00;")
        btn_key.setToolTip("Add API Key")
        btn_key.clicked.connect(self._open_api_key_dialog)

        btn_user = QPushButton("👤")
        btn_user.setFixedSize(32, 32)
        btn_user.setStyleSheet("background:#1A1C28; border:1px solid #282B3D; border-radius:16px; font-size:14px;")

        header_layout.addWidget(btn_menu)
        header_layout.addLayout(brand_layout)
        header_layout.addWidget(btn_key)
        header_layout.addWidget(btn_user)
        main_layout.addLayout(header_layout)

        # ── 2. CENTERPIECE AVATAR & GREETING ────────────────────────────
        avatar_box = QVBoxLayout()
        avatar_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_box.setSpacing(8)

        self.avatar = DistaAvatar()
        avatar_box.addWidget(self.avatar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.lbl_greeting = QLabel("Hello! I'm Dista. How can I\nassist you today?")
        self.lbl_greeting.setObjectName("greeting_label")
        self.lbl_greeting.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_box.addWidget(self.lbl_greeting)

        # Audio Waveform Visualizer
        self.waveform = DistaWaveform()
        avatar_box.addWidget(self.waveform, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(avatar_box)

        # ── 3. MAIN SECTION TABS (GRID / CHATS) ─────────────────────────
        self.section_tabs = QTabWidget()
        
        # TAB 1: TOOL INTEGRATIONS (2x2 GRID MATCHING SCREENSHOT)
        tab_grid = QWidget()
        grid_layout = QVBoxLayout(tab_grid)
        grid_layout.setContentsMargins(0, 8, 0, 0)
        
        lbl_section1 = QLabel("TOOL INTEGRATIONS")
        lbl_section1.setStyleSheet("color:#64748B; font-size:10px; font-weight:800; letter-spacing:1px;")
        grid_layout.addWidget(lbl_section1)

        grid_cards = QGridLayout()
        grid_cards.setSpacing(10)

        # Email Card
        card_email = self._create_tool_card("✉️", "Email", "Check Emails\nUnread: 3", lambda: self._on_card_click("show_emails"))
        # Docs Card
        card_docs = self._create_tool_card("📄", "Docs", "Open Documents\nRecent: 5", lambda: self._on_card_click("show_docs"))
        # Messages Card
        card_msg = self._create_tool_card("💬", "Messages", "Send Messages\nNotifications: 2", lambda: self._on_card_click("show_messages"))
        # Schedule Card
        card_sched = self._create_tool_card("📅", "Schedule", "View Schedule\nEvents: 4", lambda: self._on_card_click("show_schedule"))

        grid_cards.addWidget(card_email, 0, 0)
        grid_cards.addWidget(card_docs, 0, 1)
        grid_cards.addWidget(card_msg, 1, 0)
        grid_cards.addWidget(card_sched, 1, 1)

        grid_layout.addLayout(grid_cards)
        self.section_tabs.addTab(tab_grid, "Tools")

        # TAB 2: RECENT CHATS (MATCHING SCREENSHOT 1)
        tab_chats = QWidget()
        chats_layout = QVBoxLayout(tab_chats)
        chats_layout.setContentsMargins(0, 8, 0, 0)

        lbl_section2 = QLabel("RECENT CHATS")
        lbl_section2.setStyleSheet("color:#64748B; font-size:10px; font-weight:800; letter-spacing:1px;")
        chats_layout.addWidget(lbl_section2)

        self.chat_list = QListWidget()
        self.chat_list.setObjectName("chat_history_list")
        self._add_recent_chat_item("✉️", "Draft Email to Team", "7 hours ago · 16:14")
        self._add_recent_chat_item("📄", "Summarize Project Proposal", "7 hours ago · 13:42")
        self._add_recent_chat_item("📅", "Schedule Meeting", "5 hours ago · 13:38")
        chats_layout.addWidget(self.chat_list)

        self.section_tabs.addTab(tab_chats, "Recent Chats")

        main_layout.addWidget(self.section_tabs, 1)

        # ── 4. BOTTOM INPUT CAPSULE BAR (MATCHING SCREENSHOT) ───────────
        input_capsule = QFrame()
        input_capsule.setObjectName("input_capsule")
        capsule_layout = QHBoxLayout(input_capsule)
        capsule_layout.setContentsMargins(12, 4, 4, 4)

        self.input_field = QLineEdit()
        self.input_field.setObjectName("input_field")
        self.input_field.setPlaceholderText("Ask Dista anything...")
        self.input_field.returnPressed.connect(self._on_text_submitted)
        capsule_layout.addWidget(self.input_field)

        self.btn_mic = QPushButton("🎤")
        self.btn_mic.setObjectName("btn_mic_circle")
        self.btn_mic.clicked.connect(self._toggle_voice_input)
        capsule_layout.addWidget(self.btn_mic)

        main_layout.addWidget(input_capsule)

    def _create_tool_card(self, icon_str: str, title: str, desc: str, callback) -> QFrame:
        card = QFrame()
        card.setObjectName("tool_grid_card")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        header = QHBoxLayout()
        lbl_icon = QLabel(icon_str)
        lbl_icon.setStyleSheet("font-size:18px;")
        lbl_title = QLabel(title)
        lbl_title.setObjectName("card_title")
        header.addWidget(lbl_icon)
        header.addWidget(lbl_title)
        header.addStretch()

        lbl_desc = QLabel(desc)
        lbl_desc.setObjectName("card_desc")

        layout.addLayout(header)
        layout.addWidget(lbl_desc)

        card.mousePressEvent = lambda e: callback()
        return card

    def _add_recent_chat_item(self, icon_str: str, title: str, subtitle: str):
        item = QListWidgetItem(f"{icon_str}  {title}\n    {subtitle}")
        self.chat_list.addItem(item)

    # ── LOGIC & HANDLERS ──────────────────────────────────────────────

    def _open_api_key_dialog(self):
        key, ok = QInputDialog.getText(self, "API Key Settings", "Enter your OpenRouter or Gemini API Key:")
        if ok and key.strip():
            self.brain.openrouter_key = key.strip()
            os.environ["OPENROUTER_API_KEY"] = key.strip()
            msg = "API Key saved! Dista AI is now supercharged."
            self.lbl_greeting.setText(msg)
            self.speak(msg)

    def _speak_greeting(self):
        text = "Hello! I'm Dista. How can I assist you today?"
        self.speak(text)

    def _on_text_submitted(self):
        text = self.input_field.text().strip()
        if not text:
            return
        self.input_field.clear()

        # Set avatar & waveform to thinking state
        self.avatar.set_state(DistaAvatar.THINKING)
        self.waveform.set_active(True)

        QTimer.singleShot(150, lambda: self._process_input(text))

    def _process_input(self, text: str):
        result = self.brain.process_input(text)
        reply = result["reply"]
        self.lbl_greeting.setText(reply)
        self.speak(reply)

    def _on_card_click(self, action_code: str):
        if action_code == "show_emails":
            unread = EmailTool.get_unread_emails()
            msg = f"You have {len(unread)} unread emails." if unread else "Inbox is clear."
            self.lbl_greeting.setText(msg)
            self.speak(msg)
        elif action_code == "show_docs":
            docs = DocsTool.list_documents()
            msg = f"Found {len(docs)} documents in workspace."
            self.lbl_greeting.setText(msg)
            self.speak(msg)
        elif action_code == "show_messages":
            msgs = MessagesTool.get_recent_messages()
            msg = f"Recent message: '{msgs[0]['message']}'" if msgs else "No messages."
            self.lbl_greeting.setText(msg)
            self.speak(msg)
        elif action_code == "show_schedule":
            msg = "Your schedule has 4 events planned for today."
            self.lbl_greeting.setText(msg)
            self.speak(msg)

    def speak(self, text: str):
        if self.tts_worker and self.tts_worker.isRunning():
            self.tts_worker.terminate()

        self.tts_worker = TTSWorker(text)
        self.tts_worker.started_speaking.connect(self._on_speech_started)
        self.tts_worker.finished_speaking.connect(self._on_speech_finished)
        self.tts_worker.start()

    def _on_speech_started(self):
        self.avatar.set_state(DistaAvatar.SPEAKING)
        self.waveform.set_active(True)

    def _on_speech_finished(self):
        self.avatar.set_state(DistaAvatar.IDLE)
        self.waveform.set_active(False)

    def _toggle_voice_input(self):
        if self.stt_worker and self.stt_worker.isRunning():
            return

        self.avatar.set_state(DistaAvatar.LISTENING)
        self.waveform.set_active(True)
        self.lbl_greeting.setText("Listening...")

        self.stt_worker = STTWorker()
        self.stt_worker.recognized_text.connect(self._on_voice_recognized)
        self.stt_worker.error_occurred.connect(self._on_voice_error)
        self.stt_worker.listening_finished.connect(self._on_voice_finished)
        self.stt_worker.start()

    def _on_voice_recognized(self, text: str):
        self.input_field.setText(text)
        self._on_text_submitted()

    def _on_voice_error(self, err: str):
        self.lbl_greeting.setText(f"Mic Notice: {err}")

    def _on_voice_finished(self):
        if self.avatar.state == DistaAvatar.LISTENING:
            self.avatar.set_state(DistaAvatar.IDLE)
            self.waveform.set_active(False)


def main():
    app = QApplication(sys.argv)
    window = DistaApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
