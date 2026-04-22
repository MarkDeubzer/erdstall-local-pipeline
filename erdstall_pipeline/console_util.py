import itertools
import sys
import threading
import time


import itertools
import sys
import threading
import time


class Spinner:
    def __init__(self, message: str = "Processing", stream=None, interval: float = 0.1):
        self.message = message
        self.stream = stream or sys.stderr
        self.interval = interval

        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._last_line_length = 0

    def _write(self, text: str) -> None:
        with self._lock:
            self.stream.write(text)
            self.stream.flush()

    def _clear_line(self) -> None:
        with self._lock:
            self.stream.write("\r" + (" " * self._last_line_length) + "\r")
            self.stream.flush()
            self._last_line_length = 0

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()

        def run() -> None:
            for char in itertools.cycle("|/-\\"):
                if self._stop_event.is_set():
                    break

                line = f"{self.message}... {char}"
                padded = "\r" + line

                with self._lock:
                    self.stream.write(padded)
                    if len(line) < self._last_line_length:
                        self.stream.write(" " * (self._last_line_length - len(line)))
                    self.stream.flush()
                    self._last_line_length = len(line)

                time.sleep(self.interval)

            self._clear_line()

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop(self, final_message: str | None = None) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            self._thread = None

        if final_message:
            self._write(final_message + "\n")

    def update(self, message: str) -> None:
        self.message = message

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.stop(f"{self.message} done")
        else:
            self.stop(f"{self.message} failed")