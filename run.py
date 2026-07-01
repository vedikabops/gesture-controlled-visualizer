import subprocess
import sys


proc1 = subprocess.Popen([sys.executable, "hand-track/detect_hand.py"])
proc2 = subprocess.Popen([sys.executable, "visualizer/main.py"])

try:
    proc1.wait()
    proc2.wait()
except KeyboardInterrupt:
    proc1.terminate()
    proc2.terminate()
    proc1.wait()
    proc2.wait()