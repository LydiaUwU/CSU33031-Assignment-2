# Service application to send and receive packets between running applications and the network
# Author: Lydia MacBride

import threading
import application
from tools import *


# Variables
ext_port = 51510
loc_port = 51511
app_port = 51512
buff_size = 4096
subnet = ""
ext = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
loc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
name = ""
ext_type = "endpoint"
running = True
debug = False
controller = "a2-controller"
controller_ip = ""

# Queues
outgoing = list()

# Connected devices
connections = dict()  # { <NAME>: <NEXT_IP> }
new_route = ""


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

        global running, debug, loc, buff_size, outgoing, new_route
        while running:
            data, address = loc.recvfrom(buff_size)
            pck = tlv_dec(data)
            print_d(debug, pck)

            # When messages are received from app
            if "recipient" in pck:
                rec = pck.get("recipient")
                print_d(debug, rec + ": " + pck.get("name") + ": " + pck.get("string"))

                # If recipient in routing table
                if rec in connections:
                    outgoing.append((data, connections.get(rec)))

                # Recipient not found, contact controller
                else:
                    print_d(debug, "Recipient not found")
                    new_route = rec
                    connections.update({new_route: None})

                    outgoing.append((route_req_enc(rec, None), (controller_ip, ext_port)))

                    # Wait for routing information
                    while connections.get(new_route) is None:
                        print_d(debug, "Awaiting package route")

                    # Send to newly routed device
                    if connections.get(rec) != "None":
                        outgoing.append((data, connections.get(rec)))
                    else:
                        print_d(debug, "Unknown recipient")

            # Exit signal received
            elif "exit" in pck:
                print("Exit signal received")
                running = False

    pass


# Packet Reception Thread
class RecPackets(threading.Thread):
    def run(self):
        print("External packet reception thread starting")

        global running, ext, loc, connections, new_route
        while running:
            data, address = ext.recvfrom(buff_size)
            pck = tlv_dec(data)
            print_d(debug, pck)

            # Message packet received, forward to app
            if "name" and "string" in pck:
                loc.sendto(data, ('localhost', app_port))

            # Routing information packets
            if "route" in pck:
                connections[new_route] = pck.get("route")

    pass


# Packet Message Sending Thread
# TODO: Use combination packet type to bundle outgoing packets to one sender
class SendPackets(threading.Thread):
    def run(self):
        print("External packet sending thread starting")

        global running, ext
        while running:
            for pck in outgoing:
                print_d(debug, "Sending: " + str(pck[0]) + " to: " + pck[1][0])
                ext.sendto(pck[0], pck[1])

                outgoing.remove(pck)

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

    # Find subnet
    global subnet
    subnet = get_subnet(socket.gethostbyname(socket.gethostname()))

    # Connect to network controller and get and send username
    print("Obtaining controller IP")

    global controller, controller_ip
    while True:
        try:
            controller_ip = socket.gethostbyname(controller)
        except socket.gaierror:
            continue
        break

    # Send new packet to controller
    # TODO: Use packet sending thread and wait for acknowledgement
    ext.sendto(new_enc(ext_type, name), (controller_ip, ext_port))

    # Scan for devices on network and send information to controller
    ext_devs = find_devices("endpoint", subnet)
    ext_devs.append(find_devices("router", subnet))

    for dev in ext_devs:
        ext.sendto(dev, (controller_ip, ext_port))

    # Start application thread
    app = Application()
    app.start()

    # Start application message reception thread
    app_rep = AppReception()
    app_rep.start()

    # Start external packet reception thread
    rec_packets = RecPackets()
    rec_packets.start()

    # Start external packet sending thread
    send_packets = SendPackets()
    send_packets.start()

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
