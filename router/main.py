# Router device, routes incoming packets towards their destination
# Author: Lydia MacBride

import socket
import threading
import time
from tools import *


# Variables
port = 51510
buff_size = 4096
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ext_type = "router"
running = True

# Queues
outgoing = list()

# TODO: This is temporary for the purposes of submission 1
devices = dict()


# Packet reception (not run in a thread because packet reception gets weird when threaded)
class RecPackets(threading.Thread):
    def run(self):
        print("Packet reception thread starting")

        global running, port, s, buff_size, devices
        while running:
            data, address = s.recvfrom(buff_size)
            pck = tlv_dec(data)

            print(pck)

            # If first time receiving packet from name append to dictionary
            if pck.get("name") not in devices:
                devices.update({pck.get("name"): address})
                print(devices)

            # TODO: For submission 1, hardcoded packet forwarding, this will change with name target parameter
            if pck.get("name") == "alice" and "string" in pck:
                outgoing.append((data, devices.get("bob")))
            elif pck.get("name") == "bob" and "string" in pck:
                outgoing.append((data, devices.get("alice")))

    pass


# Packet sending thread
class SendPackets(threading.Thread):
    def run(self):
        print("Packet sending thread starting")

        global running, s, outgoing
        while running:
            for pck in outgoing:
                print("Sending: " + str(pck[0]) + " to: " + str(pck[1]))

                s.sendto(pck[0], pck[1])

                outgoing.remove(pck)

            time.sleep(1)

    pass


# Main, handles initialisation and manages threads.
def main():
    print(__name__)

    # Initialising socket
    print("Initialising socket")
    global s, port
    s.bind(('0.0.0.0', port))

    # Launch packet reception thread
    rec_packets = RecPackets()
    rec_packets.start()

    # Launch packet sending thread
    send_packets = SendPackets()
    send_packets.start()


# Run main if script run at top level
if __name__ == "__main__":
    main()
