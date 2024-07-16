import psutil
import pygetwindow as gw

# List all windows
def detect_windows():
    windows = gw.getAllTitles()
    open_windows = [window for window in windows if window]
    print("Open Windows:")
    for window in open_windows:
        print(window)

    return open_windows



