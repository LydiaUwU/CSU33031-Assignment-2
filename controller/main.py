# Network controller
# Handles device address assignment and providing routing infomation for devices with unknown recpient
# Author: Lydia MacBride

import socket
import threading
import time
from tools import *

# Variables
port = 51510
buff_size = 4096
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
running = True

# Queues
incoming = list()
outgoing = list()

# Device dictionaries
endpoints = dict()


# TODO: Packet reception thread
class RecPackets(threading.Thread):
    def run(self):
        print("Packet reception thread starting")

        global running
        while running:
            data, address = s.recvfrom(buff_size)
            pck = tlv_dec(data)

            # New device on network
            if "new" in pck:
                # TODO: Check device type
                endpoints.update({pck.get("name"): address})

                # TODO: For part 1 purposes connect all known devices
                for name in endpoints:
                    outgoing.append((new_enc("endpoint", name), (endpoints[name], port)))

    pass


# Packet sending thread
class SendPackets(threading.Thread):
    def run(self):
        print("Packet sending thread starting")

        global running, s
        while running:
            for pck in outgoing:
                s.sendto(pck[0], pck[1])

            time.sleep(1.0)

    pass


# Main loop, handles instantiation and thread management
def main():
    print(__name__)

    # Initialise socket
    print("Initialising socket")
    global port
    s.bind(("0.0.0.0", port))

    # Start packet reception thread
    rec_packets = RecPackets()
    rec_packets.start()

    # Start packet sending thread
    send_packets = SendPackets()
    send_packets.start()

    # TODO: Exit signal


# For debug purposes, run main if script run at top level
if __name__ == "__main__":
    main()
