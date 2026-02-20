import pygetwindow as gw
from pygetwindow._pygetwindow_win import Win32Window
import win32gui
import win32process
import psutil

def hwnd_to_pid(hwnd: int) -> int:
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid

def pid_to_exe(pid: int) -> str | None:
    try:
        return psutil.Process(pid).exe()
    except Exception:
        return None



def get_all_windows_names()->list[str]:
    '''
    Gets names of all open windows that have non-blank titles.
    '''
    titles = []
    for window in gw.getAllWindows():
        title = window.title.strip()
        if title:
            titles.append(title)
    return titles

def get_all_windows_objects()->list[gw.Window]:
    '''
    Gets all open windows.
    '''
    return gw.getAllWindows()

def get_all_windows_that_have_titles()->list[gw.Window]:
    '''
    Gets all open windows that have non-blank titles.
    '''
    return [window for window in gw.getAllWindows() if window.title.strip()]

def get_windows_structured_data()->list[dict]:
    '''
    Gets all open windows with their titles and HWNDs.
    '''
    for window in gw.getAllWindows():
        pid = hwnd_to_pid(window._hWnd)
        print(pid)
        exe = pid_to_exe(pid)
        print(exe)
        title = window.title
        hwnd = window._hWnd
        yield {'title': title, 'hwnd': hwnd, 'exe': exe}

def get_windows_titles_matching_string(string:str)->list[str]:
    '''
    Gets names of all open windows that contain the given string in their titles.
    '''
    return [window.title for window in gw.getWindowsWithTitle(string)]

def get_window_object_matching_string(string:str)->list[gw.Window]:
    '''
    Gets the window object that contains the given string in its title.
    '''
    return gw.getWindowsWithTitle(string)

def open_window(hwnd:int)->None:
    '''
    Opens the window with the given HWND.
    '''
    w = Win32Window(hwnd)
    w.activate()