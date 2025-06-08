from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from pypresence import Presence
import os
import sys
import time


class RichPresenceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Discord RPC")
        self.setFixedSize(350, 325)
        self.rpc = None

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()
        basedir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        pixmap = QPixmap(os.path.join(basedir, "Discord-logo.png"))
        scaled_pixmap = pixmap.scaledToWidth(self.width() - 40, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        self.app_id_input = QLineEdit()
        self.app_id_input.setPlaceholderText("Discord App ID")
        layout.addWidget(self.app_id_input)

        self.label = QLabel("Set your Discord Rich Presence description:")
        self.top_input = QLineEdit()
        self.top_input.setPlaceholderText("First line (optional)")
        self.bottom_input = QLineEdit()
        self.bottom_input.setPlaceholderText("Second line (optional)")

        layout.addWidget(self.label)
        layout.addWidget(self.top_input)
        layout.addWidget(self.bottom_input)

        self.submit_button = QPushButton("Submit")
        self.close_button = QPushButton("Close")
        layout.addWidget(self.submit_button)
        layout.addWidget(self.close_button)

        footer_label = QLabel("Tool by digitalgoggles")
        footer_label.setAlignment(Qt.AlignRight)
        footer_label.setStyleSheet("font-size: 10px; color: gray; padding-top: 5px;")
        layout.addWidget(footer_label)

        self.setLayout(layout)

        self.submit_button.clicked.connect(self.update_presence)
        self.close_button.clicked.connect(self.close)  # Now closes the app

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("Discord-logo.png"))
        self.tray_icon.setToolTip("Discord RPC is running")

        tray_menu = QMenu()
        restore_action = QAction("Restore", self)
        quit_action = QAction("Quit", self)

        restore_action.triggered.connect(self.showNormal)
        quit_action.triggered.connect(self.close)

        tray_menu.addAction(restore_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.messageClicked.connect(self.showNormal)

    def update_presence(self):
        app_id = self.app_id_input.text().strip()
        top_line = self.top_input.text().strip()
        bottom_line = self.bottom_input.text().strip()

        if not app_id:
            self.label.setText("App ID is required.")
            return

        if self.rpc is None:
            try:
                self.rpc = Presence(app_id)
                self.rpc.connect()
            except Exception as e:
                self.label.setText("Failed to connect to Discord.")
                print(f"Connection error: {e}")
                return

        payload = {}
        if top_line:
            payload["details"] = top_line
        if bottom_line:
            payload["state"] = bottom_line
        if payload:
            payload["start"] = time.time()

        try:
            self.rpc.update(**payload)
            self.label.setText("Presence updated.")
        except Exception as e:
            self.label.setText("Failed to update presence.")
            print(f"Update error: {e}")

    def closeEvent(self, event):
        """Ensure full cleanup on close (any method of quitting)."""
        if self.rpc:
            try:
                self.rpc.clear()
                self.rpc.close()
            except:
                pass
        self.tray_icon.hide()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RichPresenceApp()
    window.show()
    sys.exit(app.exec_())
