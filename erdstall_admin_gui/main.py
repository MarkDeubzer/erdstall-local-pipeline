from __future__ import annotations
import sys
import time
import qdarktheme

t0 = time.time()
print("1 start")

from PySide6.QtWidgets import QApplication
print("2 QApplication", time.time() - t0)

from PySide6.QtCore import QTimer
print("3 QTimer", time.time() - t0)

from PySide6.QtGui import QIcon
print("4 QIcon", time.time() - t0)

from erdstall_admin_gui.windows.splash_screen import SplashScreen
print("5 SplashScreen", time.time() - t0)

from erdstall_admin_gui.windows.main_window import MainWindow
print("6 MainWindow", time.time() - t0)


def main() -> int:
    print("7 creating app", time.time() - t0)
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("dark")

    print("8 creating splash", time.time() - t0)
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    print("9 creating main window", time.time() - t0)
    main_window = MainWindow()

    print("10 main window created", time.time() - t0)

    progress_timer = QTimer()
    progress_value = {"value": 0}

    def update_progress() -> None:
        progress_value["value"] += 9
        splash.progress_bar.setValue(progress_value["value"])
        if progress_value["value"] >= 100:
            progress_timer.stop()
            splash.close()
            main_window.show()

    progress_timer.timeout.connect(update_progress)
    progress_timer.start(100)

    print("11 entering event loop", time.time() - t0)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())