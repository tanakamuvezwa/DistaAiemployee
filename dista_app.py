import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QTabWidget, QFrame,
    QSplitter, QListWidget, QListWidgetItem, QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont

from dista_avatar import DistaAvatar
from dista_voice import TTSWorker, STTWorker
from dista_brain import DistaBrain
from dista_tools import EmailTool, DocsTool, MessagesTool


class DistaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dista AI — Local Desktop Assistant")
        self.resize(1000, 780)
        self.setMinimumSize(850, 650)

        # Core Components
        self.brain = DistaBrain()
        self.tts_worker = None
        self.stt_worker = None

        # Load QSS Style
        qss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dista_style.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

        self._init_ui()

        # Initial Greeting
        QTimer.singleShot(500, self._speak_greeting)

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # ── 1. TOP AVATAR HUD SECTION ──────────────────────────────────
        top_hud = QFrame()
        top_hud.setObjectName("tool_card")
        top_layout = QVBoxLayout(top_hud)
        top_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.setContentsMargins(10, 10, 10, 10)

        # Title Tag
        title_lbl = QLabel("DISTA AI // LOCAL OFFLINE INTERFACE")
        title_lbl.setObjectName("status_label")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(title_lbl)

        # Pixel Avatar
        self.avatar = DistaAvatar()
        top_layout.addWidget(self.avatar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Avatar Status Badge
        self.state_label = QLabel("SYSTEM IDLE // AWAITING COMMAND")
        self.state_label.setStyleSheet("color: #8C94A8; font-weight: bold; font-size: 11px;")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(self.state_label)

        main_layout.addWidget(top_hud)

        # ── 2. TOOL SHORTCUT CARDS & WORKSPACE TABS ────────────────────
        shortcuts_layout = QHBoxLayout()
        shortcuts_layout.setSpacing(12)

        # Shortcut Tiles
        btn_email_card = QPushButton("📧 Emails\n(3 Local)")
        btn_email_card.setMinimumHeight(54)
        btn_email_card.clicked.connect(lambda: self.tabs.setCurrentIndex(0))

        btn_docs_card = QPushButton("📄 Docs\n(Workspace Files)")
        btn_docs_card.setMinimumHeight(54)
        btn_docs_card.clicked.connect(lambda: self.tabs.setCurrentIndex(1))

        btn_msg_card = QPushButton("💬 Messages\n(Local Inbox)")
        btn_msg_card.setMinimumHeight(54)
        btn_msg_card.clicked.connect(lambda: self.tabs.setCurrentIndex(2))

        shortcuts_layout.addWidget(btn_email_card)
        shortcuts_layout.addWidget(btn_docs_card)
        shortcuts_layout.addWidget(btn_msg_card)

        main_layout.addLayout(shortcuts_layout)

        # Workspace Tab Widget
        self.tabs = QTabWidget()

        # TAB 1: EMAILS
        self.tab_email = QWidget()
        email_layout = QHBoxLayout(self.tab_email)
        self.email_list = QListWidget()
        self.email_list.itemClicked.connect(self._on_email_selected)
        self.email_preview = QTextEdit()
        self.email_preview.setReadOnly(True)
        email_layout.addWidget(self.email_list, 1)
        email_layout.addWidget(self.email_preview, 2)
        self.tabs.addTab(self.tab_email, "📧 Email Center")

        # TAB 2: DOCUMENTS
        self.tab_docs = QWidget()
        docs_layout = QHBoxLayout(self.tab_docs)
        self.docs_list = QListWidget()
        self.docs_list.itemClicked.connect(self._on_doc_selected)
        self.doc_editor = QTextEdit()
        docs_layout.addWidget(self.docs_list, 1)
        docs_layout.addWidget(self.doc_editor, 2)
        self.tabs.addTab(self.tab_docs, "📄 Workspace Docs")

        # TAB 3: MESSAGES & CHAT STREAM
        self.tab_msg = QWidget()
        msg_layout = QVBoxLayout(self.tab_msg)
        self.chat_stream = QTextEdit()
        self.chat_stream.setReadOnly(True)
        msg_layout.addWidget(self.chat_stream)
        self.tabs.addTab(self.tab_msg, "💬 Command Stream & Inbox")

        main_layout.addWidget(self.tabs, 1)

        # ── 3. BOTTOM INPUT BAR (TEXT + VOICE) ─────────────────────────
        input_frame = QFrame()
        input_frame.setObjectName("tool_card")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(8, 8, 8, 8)

        # Mic Button
        self.btn_mic = QPushButton("🎤 Voice")
        self.btn_mic.setObjectName("btn_mic")
        self.btn_mic.clicked.connect(self._toggle_voice_input)
        input_layout.addWidget(self.btn_mic)

        # Text Input
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask Dista anything... (e.g. 'summarize emails', 'read docs', 'hello')")
        self.input_field.returnPressed.connect(self._on_text_submitted)
        input_layout.addWidget(self.input_field)

        # Transmit Button
        self.btn_send = QPushButton("Transmit ➔")
        self.btn_send.setObjectName("btn_primary")
        self.btn_send.clicked.connect(self._on_text_submitted)
        input_layout.addWidget(self.btn_send)

        main_layout.addWidget(input_frame)

        # Load Data into UI
        self._refresh_emails()
        self._refresh_docs()
        self._refresh_messages()

    # ── EVENT HANDLERS & LOGIC ─────────────────────────────────────────

    def _speak_greeting(self):
        text = "Systems operational. I am Dista AI, running 100% locally on your machine."
        self._append_chat("DISTA AI", text)
        self.speak(text)

    def _on_text_submitted(self):
        user_text = self.input_field.text().trim() if hasattr(self.input_field.text(), 'trim') else self.input_field.text().strip()
        if not user_text:
            return
        self.input_field.clear()

        # Display user input
        self._append_chat("YOU", user_text)

        # Set Avatar to THINKING
        self.avatar.set_state(DistaAvatar.THINKING)
        self.state_label.setText("PROCESSING INTENT...")

        # Process in brain
        QTimer.singleShot(150, lambda: self._process_brain(user_text))

    def _process_brain(self, user_text: str):
        result = self.brain.process_input(user_text)
        reply = result["reply"]
        action = result.get("action")

        self._append_chat("DISTA AI", reply)

        # Switch tabs if action returned
        if action == "show_emails":
            self.tabs.setCurrentIndex(0)
            self._refresh_emails()
        elif action == "show_docs":
            self.tabs.setCurrentIndex(1)
            self._refresh_docs()
        elif action == "show_messages":
            self.tabs.setCurrentIndex(2)
            self._refresh_messages()

        # Speak back
        self.speak(reply)

    def speak(self, text: str):
        """Triggers pyttsx3 in background thread"""
        if self.tts_worker and self.tts_worker.isRunning():
            self.tts_worker.terminate()

        self.tts_worker = TTSWorker(text)
        self.tts_worker.started_speaking.connect(self._on_speech_started)
        self.tts_worker.finished_speaking.connect(self._on_speech_finished)
        self.tts_worker.start()

    def _on_speech_started(self):
        self.avatar.set_state(DistaAvatar.SPEAKING)
        self.state_label.setText("SPEAKING...")

    def _on_speech_finished(self):
        self.avatar.set_state(DistaAvatar.IDLE)
        self.state_label.setText("SYSTEM IDLE // AWAITING COMMAND")

    def _toggle_voice_input(self):
        if self.stt_worker and self.stt_worker.isRunning():
            return

        self.avatar.set_state(DistaAvatar.LISTENING)
        self.state_label.setText("LISTENING TO MICROPHONE...")
        self.btn_mic.setProperty("active", "true")
        self.btn_mic.setStyle(self.btn_mic.style())

        self.stt_worker = STTWorker()
        self.stt_worker.recognized_text.connect(self._on_voice_recognized)
        self.stt_worker.error_occurred.connect(self._on_voice_error)
        self.stt_worker.listening_finished.connect(self._on_voice_finished)
        self.stt_worker.start()

    def _on_voice_recognized(self, text: str):
        self.input_field.setText(text)
        self._on_text_submitted()

    def _on_voice_error(self, err_msg: str):
        self.state_label.setText(f"MIC NOTICE: {err_msg}")

    def _on_voice_finished(self):
        self.btn_mic.setProperty("active", "false")
        self.btn_mic.setStyle(self.btn_mic.style())
        if self.avatar.state == DistaAvatar.LISTENING:
            self.avatar.set_state(DistaAvatar.IDLE)
            self.state_label.setText("SYSTEM IDLE // AWAITING COMMAND")

    # ── DATA POPULATION HELPERS ────────────────────────────────────────

    def _append_chat(self, sender: str, message: str):
        timestamp = QTimer.singleShot
        fmt = f"<div style='margin-bottom:8px;'><b><span style='color:#FF6B00;'>[{sender}]</span>:</b> {message}</div>"
        self.chat_stream.append(fmt)

    def _refresh_emails(self):
        self.email_list.clear()
        emails = EmailTool.get_all_emails()
        for e in emails:
            item = QListWidgetItem(f"[{e['priority']}] {e['sender']} — {e['subject']}")
            item.setData(Qt.ItemDataRole.UserRole, e)
            self.email_list.addItem(item)
        if emails:
            self.email_list.setCurrentRow(0)
            self._on_email_selected(self.email_list.item(0))

    def _on_email_selected(self, item):
        if not item:
            return
        e = item.data(Qt.ItemDataRole.UserRole)
        self.email_preview.setHtml(f"""
            <h3 style="color:#FF6B00;">{e['subject']}</h3>
            <p><b>From:</b> {e['sender']} | <b>Priority:</b> {e['priority']} | <b>Time:</b> {e['timestamp']}</p>
            <hr style="border:1px solid #282B3D;"/>
            <p style="font-size:14px;line-height:1.5;">{e['body']}</p>
        """)

    def _refresh_docs(self):
        self.docs_list.clear()
        docs = DocsTool.list_documents()
        for d in docs:
            self.docs_list.addItem(d)
        if docs:
            self.docs_list.setCurrentRow(0)
            self._on_doc_selected(self.docs_list.item(0))

    def _on_doc_selected(self, item):
        if not item:
            return
        filename = item.text()
        content = DocsTool.read_document(filename)
        self.doc_editor.setPlainText(content)

    def _refresh_messages(self):
        msgs = MessagesTool.get_recent_messages()
        for m in reversed(msgs):
            self._append_chat(m['contact'] if m['direction'] == 'INCOMING' else 'YOU', m['message'])


def main():
    app = QApplication(sys.argv)
    window = DistaApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
