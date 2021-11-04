# Service application to send and receive packets between running applications and the network
# Author: Lydia MacBride

import socket
import threading
import time
import application
from tools import *


# Variables
ext_port = 51510
loc_port = 51511
app_port = 51512
buff_size = 4096
ext = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
loc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
name = ""
ext_type = "endpoint"
running = True
debug = False
controller = "a2-controller"
controller_ip = ""

# Queues
incoming = list()
outgoing = list()

# Devices
# TODO: This is for the purposes of part 1, will be removed/converted to dealing with routers
endpoints = dict()


# Application thread
class Application(threading.Thread):
    def run(self):
        global name
        application.main(name)

    pass


# Application message reception thread
class AppReception(threading.Thread):
    def run(self):
        print("Application message reception thread starting")

        global running, debug, loc, outgoing
        while running:
            data, address = loc.recvfrom(buff_size)
            msg = tlv_dec(data)
            print_d(debug, msg)

            # When messages are received
            # TODO: Forward messages to external network
            if "name" in msg:
                print_d(debug, msg.get("name") + ": " + msg.get("string"))
                # TODO: This is a hack
                outgoing.append((data, (endpoints.get("ip"), ext_port)))

            # Exit signal received
            elif "exit" in msg:
                print("Exit signal received")
                running = False

    pass


# Packet Reception Thread
class RecPackets(threading.Thread):
    def run(self):
        print("External packet reception thread starting")

        global running, ext, loc
        while running:
            data, address = ext.recvfrom(buff_size)
            pck = tlv_dec(data)
            print_d(debug, pck)

            # Message packet received, forward to app
            if "name" and "string" in pck:
                loc.sendto(data, ('localhost', app_port))

    pass


# Packet Message Sending Thread
# TODO: Use combination packet type to bundle outgoing packets to one sender
class SendPackets(threading.Thread):
    def run(self):
        print("External packet sending thread starting")

        global running, ext
        while running:
            for pck in outgoing:
                ext.sendto(pck[0], pck[1])

            time.sleep(1)

    pass


# Main function, will handle launching and managing various threads
def main():
    print(__name__)

    # Request username
    global name
    name = input("Enter your name: ")
    print("Your name is: " + name)

    # Initialising socket
    print("Initialising socket")
    global loc_port, ext_port
    loc.bind(('localhost', loc_port))
    ext.bind(('0.0.0.0', ext_port))

    # TODO: Connect to network controller and get and send username
    """
    print("Obtaining controller IP")
    global controller_ip

    while True:
        try:
            controller_ip = socket.gethostbyname(controller)
        except socket.gaierror:
            continue
        break
    

    # Send new packet to controller
    # TODO: Use packet sending thread and wait for acknowledgement
    ext.sendto(new_enc(ext_type, name), (controller_ip, ext_port))
    """

    # TODO: Remove this for future parts
    # This is a very hacky way to get two endpoints talking to each other!!!!
    # This will not be used in the final submission
    hostname = socket.gethostname()
    print("Hostname is: " + hostname)
    global endpoints
    if hostname == "a2-alice":
        while True:
            try:
                bob_ip = socket.gethostbyname("a2-bob")
                endpoints.update({"ip": bob_ip})
            except socket.gaierror:
                continue
            break
    else:
        while True:
            try:
                alice_ip = socket.gethostbyname("a2-alice")
                endpoints.update({"ip": alice_ip})
            except socket.gaierror:
                continue
            break

    # Start application thread
    app = Application()
    app.start()

    # Start application message reception thread
    app_rep = AppReception()
    app_rep.start()

    # When application thread ends, rejoin threads and exit
    global running
    while True:
        if not running:
            print("Stopping threads")

            # Join threads
            app.join()
            app_rep.join()

            break

    print("Service shutdown successfully!")


# For debug purposes, run main if script run at top level
if __name__ == "__main__":
    main()
