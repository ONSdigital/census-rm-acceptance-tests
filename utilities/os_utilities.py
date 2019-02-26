import signal

import psutil
from psutil import NoSuchProcess


def get_child_processes(parent_pid):
    try:
        child_processes = psutil.Process(parent_pid).children(recursive=True)
    except NoSuchProcess:
        return

    return child_processes


def kill_all_processes(children):
    if not children:
        return

    try:
        for process in children:
            process.send_signal(signal.SIGTERM)
    except NoSuchProcess:
        pass
