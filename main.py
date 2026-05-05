import sys
from typing import Any
from PySide6.QtWidgets import QApplication, QStackedWidget, QMessageBox, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QAction
from PySide6.QtCore import QTimer

# -----------------------------
# Import your pages
# -----------------------------
from trueface.welcome_page import WelcomePage
from trueface.home_page import HomePage
from trueface.person_details_page import PersonDetailsPage
from trueface.person_history_page import PersonHistoryPage

# -----------------------------
# Import FaceEngine
# -----------------------------
from trueface.face_engine import FaceEngine
from trueface.database import FaceDatabase
from trueface.theme import Theme
from trueface.utils import get_resource_path

# -----------------------------
# TrueFace Application
# -----------------------------
class TrueFaceApp:
    def __init__(self) -> None:
        # -----------------------------
        # Create QApplication first
        # -----------------------------
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(Theme.STYLE)
        
        # Set Global Window Icon
        logo_path = get_resource_path("assets/logo.png")
        app_icon = QIcon(logo_path)
        self.app.setWindowIcon(app_icon)
        
        # -----------------------------
        # Setup System Tray (Persistence)
        # -----------------------------
        self._setup_tray(app_icon)
        
        self.stack = QStackedWidget()
        self.stack.setWindowIcon(app_icon)

        # -----------------------------
        # Initialize FaceEngine (OpenCV only)
        # -----------------------------
        try:
            self.face_engine = FaceEngine()
        except Exception as e:
            QMessageBox.critical(
                None, "FaceEngine Error", f"Failed to initialize FaceEngine:\n{e}"
            )
            sys.exit(1)

        self.db = FaceDatabase()

        # -----------------------------
        # Initialize pages
        # -----------------------------
        self._init_pages()
        self._add_pages_to_stack()
        self.stack.setCurrentIndex(0)

    # -----------------------------
    # Page initialization
    # -----------------------------
    def _init_pages(self) -> None:
        """Create all pages and setup callbacks."""

        # Welcome page just needs callback to move to home
        self.welcome_page: WelcomePage = WelcomePage(self.show_home)

        # HomePage needs FaceEngine + callback to show person details
        self.home_page: HomePage = HomePage(
            face_engine=self.face_engine,
            db=self.db,
            show_personal_details=self.show_person_details,
            show_personal_history=self.show_person_history
        )

        # Person details page needs callbacks for back navigation and history
        self.details_page: PersonDetailsPage = PersonDetailsPage(
            back_callback=self.back_to_home_from_details,
            history_callback=self.show_person_history,
            db=self.db
        )

        # History page needs callback to go back to details
        self.history_page: PersonHistoryPage = PersonHistoryPage(
            back_callback=self.back_to_details_from_history
        )

    def _add_pages_to_stack(self) -> None:
        """Add all pages to the QStackedWidget."""
        self.stack.addWidget(self.welcome_page)  # index 0
        self.stack.addWidget(self.home_page)     # index 1
        self.stack.addWidget(self.details_page)  # index 2
        self.stack.addWidget(self.history_page)  # index 3

    def _setup_tray(self, icon: QIcon) -> None:
        """Setup system tray icon and menu for persistence."""
        self.tray_icon = QSystemTrayIcon(icon, self.app)
        
        tray_menu = QMenu()
        show_action = QAction("Open TrueFace", tray_menu)
        show_action.triggered.connect(self.restore_window)
        
        quit_action = QAction("Quit Application", tray_menu)
        quit_action.triggered.connect(self.quit_app)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()
        
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.restore_window()

    def restore_window(self):
        self.stack.show()
        self.stack.activateWindow()
        self.stack.raise_()

    def quit_app(self):
        self.tray_icon.hide()
        QApplication.quit()

    # -----------------------------
    # Navigation callbacks
    # -----------------------------
    def _change_page(self, index: int) -> None:
        """Helper to switch pages."""
        self.stack.setCurrentIndex(index)

    def show_home(self) -> None:
        """Show the home page and start camera/NFC loop."""
        self._change_page(1)
        if hasattr(self.home_page, "start_timer"):
            self.home_page.start_timer()

    def show_person_details(self, person_data: Any, source: str = 'home') -> None:
        """Show the person details page."""
        if hasattr(self.home_page, "stop_timer"):
            self.home_page.stop_timer()
        
        self.details_source = source
        self.details_page.show_person(person_data, source=source)
        self._change_page(2)

    def back_to_home_from_details(self) -> None:
        """Return from details page to home page or admin panel."""
        if hasattr(self, 'details_source') and self.details_source == 'admin':
            self._change_page(1)
            QTimer.singleShot(100, self.home_page.manage_persons)
        else:
            self._change_page(1)
            if hasattr(self.home_page, "start_timer"):
                self.home_page.start_timer()

    def show_person_history(self, person_name: str, history_list: list[Any], source: str = 'details') -> None:
        """Show the history page for a specific person."""
        self.history_source = source
        self.history_page.show_history(person_name, history_list)
        self._change_page(3)

    def back_to_details_from_history(self) -> None:
        """Return from history page to details page or admin panel."""
        if hasattr(self, 'history_source') and self.history_source == 'admin':
            self._change_page(1)
            # Use a slight delay to ensure the page transition completes before opening modal
            QTimer.singleShot(100, self.home_page.manage_persons)
        else:
            self._change_page(2)

    # -----------------------------
    # Run the application
    # -----------------------------
    def run(self) -> None:
        """Start the Qt application."""
        self.stack.setWindowTitle("TrueFace Security")
        self.stack.setMinimumSize(1100, 750)
        self.stack.resize(1100, 750)
        
        # Override closeEvent to hide to tray
        def close_event(event):
            if self.tray_icon.isVisible():
                self.stack.hide()
                event.ignore()
                self.tray_icon.showMessage(
                    "TrueFace Security",
                    "Application is still running in the background.",
                    QSystemTrayIcon.Information,
                    2000
                )
            else:
                event.accept()
        
        self.stack.closeEvent = close_event
        
        self.stack.show()
        sys.exit(self.app.exec())

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    app = TrueFaceApp()
    app.run()
