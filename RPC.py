import os
import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from pypresence import Presence


class RichPresenceApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Discord RPC")
        self.setFixedSize(350, 325)
        self.rpc = None

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Load image
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(base_dir, "Discord-logo.png")
        pixmap = QPixmap(image_path).scaledToWidth(self.width() - 40, Qt.SmoothTransformation)
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        # Input fields
        self.app_id_input = QLineEdit(placeholderText="Discord App ID")
        self.top_input = QLineEdit(placeholderText="First line (optional)")
        self.bottom_input = QLineEdit(placeholderText="Second line (optional)")
        layout.addWidget(self.app_id_input)

        self.status_label = QLabel("Set your Discord Rich Presence description:")
        layout.addWidget(self.status_label)
        layout.addWidget(self.top_input)
        layout.addWidget(self.bottom_input)

        # Buttons
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.update_presence)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.close_button)

        # Footer
        footer = QLabel("Tool by Cooper F.")
        footer.setAlignment(Qt.AlignRight)
        footer.setStyleSheet("font-size: 10px; color: gray; padding-top: 5px;")
        layout.addWidget(footer)

        self.setLayout(layout)

    def update_presence(self):
        app_id = self.app_id_input.text().strip()
        if not app_id:
            self.status_label.setText("App ID is required.")
            return

        if self.rpc is None:
            try:
                self.rpc = Presence(app_id)
                self.rpc.connect()
            except Exception as e:
                self.status_label.setText("Failed to connect to Discord.")
                print(f"Connection error: {e}")
                return

        payload = {
            "details": self.top_input.text().strip(),
            "state": self.bottom_input.text().strip(),
            "start": time.time()
        }

        # Filter out empty fields
        payload = {k: v for k, v in payload.items() if v}

        try:
            self.rpc.update(**payload)
            self.status_label.setText("Presence updated.")
        except Exception as e:
            self.status_label.setText("Failed to update presence.")
            print(f"Update error: {e}")

    def closeEvent(self, event):
        if self.rpc:
            try:
                self.rpc.clear()
                self.rpc.close()
            except:
                pass
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RichPresenceApp()
    window.show()
    sys.exit(app.exec_())