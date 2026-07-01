from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
import threading

class GestureReceiver:

    def __init__(self):

        self.left = {
            "pinch_distance": 0.0,
            "pinch_angle": 0.0,
            "hand_openness": 0.0,

            "pinch": False,
            "fist": False,
            "open_hand": False,
        }

        self.right = {
            "pinch_distance": 0.0,
            "pinch_angle": 0.0,
            "hand_openness": 0.0,

            "pinch": False,
            "fist": False,
            "open_hand": False,
        }
        
        self.dispatcher = Dispatcher()
        self.dispatcher.set_default_handler(self.osc_handler)

        self.server = ThreadingOSCUDPServer(("127.0.0.1", 8000), self.dispatcher)
        self.server_thread = threading.Thread(target = self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
    
    def osc_handler(self, address, *args):
        hand, gesture = address.strip("/").split("_", 1)
        hand = hand.lower()
        value = args[0]

        if hand == "left":
            self.left[gesture] = value

        elif hand == "right":
            self.right[gesture] = value
            