import webview
import os
import threading
import subprocess
import sys
import time

def start_server():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle (packaged by PyInstaller).
        base_path = sys._MEIPASS
    else:
        # The application is run from a script.
        base_path = os.path.dirname(os.path.abspath(__file__))

    manage_py_path = os.path.join(base_path, "scheduler_project", "manage.py")
    subprocess.Popen(['python', manage_py_path, 'runserver', '127.0.0.1:8000'])

    
    if os.path.exists(manage_py_path):
        print(f"File exists at: {manage_py_path}")
    else:
        print(f"File does NOT exist at: {manage_py_path}")



if __name__ == '__main__':
    print(os.getcwd())
    # Start the Django server in a separate thread
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    time.sleep(4)  # Give server 5 seconds to start
    # Create a webview window


    webview.create_window('Scheduler App', 
                      'http://127.0.0.1:8000', 
                      resizable=True, 
                      fullscreen=False)
    
    webview.start()