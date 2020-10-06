"""Auxiliary functionality"""

from enum import Enum, auto
import time
import threading


class TaskStates(Enum):
    """Background task states"""

    STOPPED = auto()
    RUNNING = auto()
    TERMINATING = auto()


class ConsoleHeartBeat:
    """A context manager starting a heart beater printing dots to the given
       console in a thread."""

    def __init__(self, console, sleep_period_s):
        self._console = console
        self._sleep_period_s = sleep_period_s
        self._state = TaskStates.STOPPED
        self._state_lock = threading.Lock()
        self._thread = None

    def _set_state(self, new_state: TaskStates) -> TaskStates:
        with self._state_lock:
            old_state = self._state
            self._state = new_state

        return old_state

    def _run(self):
        """Starts beating"""

        old_state = self._set_state(TaskStates.RUNNING)

        if old_state != TaskStates.STOPPED:
            return

        if self._sleep_period_s <= 0:
            self._set_state(TaskStates.STOPPED)
            return

        count = 0
        dot_period = 10 * self._sleep_period_s
        line_length = 0
        elapsed = 0
        end = ''
        while self._state == TaskStates.RUNNING:
            time.sleep(self._sleep_period_s)
            end = ''

            if count == 9:
                if line_length == 7:
                    end = '\n'
                    line_length = 0
                else:
                    line_length += 1

                elapsed += dot_period
                self._console.printout(f'{elapsed}s', end=end)
                count = 0
            else:
                count += 1
                self._console.printout('.', end=end)

            self._console.flush()

        if end != '\n':
            self._console.printout('')

        self._set_state(TaskStates.STOPPED)

    def _stop(self):
        """Stops beating"""

        self._set_state(TaskStates.TERMINATING)

    def __enter__(self):
        if self._sleep_period_s > 0:
            self._thread = threading.Thread(target=self._run)
            self._thread.start()

        return self

    def __exit__(self, *exc):
        if self._thread is not None:
            self._stop()
            self._thread.join()
            self._thread = None

        return False
