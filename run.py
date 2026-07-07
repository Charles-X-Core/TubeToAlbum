import sys
import os
import subprocess
import time
import webbrowser
from threading import Thread

def start_backend():
    backend_path = os.path.join(os.path.dirname(__file__), 'backend', 'server.py')
    subprocess.Popen([sys.executable, backend_path])

def wait_for_backend(url='http://127.0.0.1:5000/api/config', retries=20):
    import urllib.request
    for _ in range(retries):
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except:
            time.sleep(0.5)
    return False

if __name__ == '__main__':
    print("Iniciando TubeToAlbum...")
    start_backend()

    if wait_for_backend():
        print("Backend listo. Abriendo Electron...")
        electron_path = os.path.join(os.path.dirname(__file__), 'electron', 'node_modules', '.bin', 'electron')
        if sys.platform == 'win32':
            electron_path += '.cmd'
        subprocess.Popen([electron_path, os.path.join(os.path.dirname(__file__), 'electron', 'main.js')])
    else:
        print("Error: Backend no respondió")
        sys.exit(1)
