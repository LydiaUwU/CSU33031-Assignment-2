# Service application to send and receive packets between running applications and the network
# Author: Lydia MacBride

import socket
import threading
import application
from tools import *


# Variables
ext_port = 51510
loc_port = 51511
app_port = 51512
buff_size = 4096
ext = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
loc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Application thread
class Application(threading.Thread):
    def run(self):
        application.main()


# Application message reception thread
class AppReception(threading.Thread):
    def run(self):
        data, address = loc.recvfrom(buff_size)
        msg = tlv_dec(data)
        print(msg[0] + ": " + msg[1])


# TODO: Message Reception Thread


# TODO: External Message Sending Thread


# Main function, will handle launching and managing various threads
def main():
    print(__name__)

    # Initialising socket
    print("Initialising socket")
    global loc_port
    loc.bind(('localhost', loc_port))

    # Start application thread
    app = Application()
    app.start()

    # Start application reception
    app_rep = AppReception()
    app_rep.start()

    # TODO: When application thread ends, rejoin threads and exit


# For debug purposes, run main if script run at top level
if __name__ == "__main__":
    main()
