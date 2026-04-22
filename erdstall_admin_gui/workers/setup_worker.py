from __future__ import annotations
from PySide6.QtCore import QObject, Signal, Slot
from erdstall_pipeline.settings.app_settings import AppSettings
import importlib


class SetupWorker(QObject):
    finished = Signal()
    log = Signal(str)
    succes = Signal(str)
    error = Signal(str)


    def __init__(self) -> None:
        super().__init__()

    @Slot()
    def run(self)-> None:
        try:
            self.log.emit("Starting environment validation...\n")
            self._check_python_modules()
            self._check_fiji()
            self.succes.emit("Setup validation completed successfully.")
        except Exception as e: 
            self.error.emit(str(e))
        finally:
            self.finished.emit()

    def _check_python_modules(self)-> None:
        required_modules = [
            ("Pillow", "PIL"),
            ("opencv-python", "cv2"),
            ("numpy", "numpy"),
            ("pymeshlab","pymeshlab"),
            ("vtk", "vtk"),
            ("scyjava","scyjava"),
            ("imagej", "imagej"),
            ("jpype1", "jpype"),
            ("scipy","scipy"),
            ("PySide6","PySide6"),
        ]

        self.log.emit("Checking Python modules...")

        missing: list[str] = []

        for package_name, import_name in required_modules:
            try:
                importlib.import_module(import_name)
                self.log.emit(f"[OK] {package_name}")
            except Exception:
                missing.append(package_name)
                self.log.emit(f"[MISSING] {package_name}")
        
        if missing:
            raise RuntimeError(
                "Missing Python packages: " + ", ".join(missing)
            )
        
    def _check_fiji(self) -> None:
        self.log.emit("Checking Fiji executable...")

        fiji_exe = AppSettings.get_fiji_exe()
        if fiji_exe is None:
            raise RuntimeError("Fiji executable is not configured.")
        
        if not fiji_exe.exists():
            raise RuntimeError(f"Configured Fiji executable not found: {fiji_exe}")
        
        if not fiji_exe.is_file():
            raise RuntimeError(f"Configured Fiji path is not a file: {fiji_exe}")

        self.log.emit(f"[OK] Fiji found at: {fiji_exe}")



