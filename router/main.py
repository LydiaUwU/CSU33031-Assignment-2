# Router device, routes incoming packets towards their destination
# Author: Lydia MacBride
# TODO: Send a device found packet for all found devices, add hostname to packets

import threading
from tools import *


# Variables
ip = ""
port = 51510
buff_size = 4096
subnet = ""
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ext_type = "router"
running = True
controller = "a2-controller"
controller_ip = ""

# Queues
outgoing = list()

# Connected devices
connections = dict()  # { <NAME>: <NEXT_HOSTNAME> }


# Packet reception (not run in a thread because packet reception gets weird when threaded)
class RecPackets(threading.Thread):
    def run(self):
        print("Packet reception thread starting")

        global running, port, s, buff_size
        while running:
            data, address = s.recvfrom(buff_size)
            pck = tlv_dec(data)
            print("\n")
            print(address)
            print(pck)

            # When messages are received
            if "recipient" in pck:
                rec = pck.get("recipient")
                print(rec + ": " + pck.get("name") + ": " + pck.get("string"))

                # If recipient in routing table
                if rec in connections:
                    outgoing.append((data, (connections.get(rec), port)))

                # Recipient not found, contact controller
                else:
                    print("Recipient not found")
                    new_route = rec
                    connections.update({new_route: None})

                    outgoing.append((route_req_enc(rec, None), (controller_ip, port)))

                    # Wait for routing information
                    while connections.get(new_route) is None:
                        print("Awaiting package route")
                        new_data, new_address = s.recvfrom(buff_size)
                        new_pck = tlv_dec(new_data)

                        # Routing information packets
                        if "route" in new_pck:
                            connections[new_route] = new_pck.get("route")

                    # Send to newly routed device
                    if connections.get(rec) != "None":
                        outgoing.append((data, (connections.get(rec), port)))
                    else:
                        print("Unknown recipient")

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

    pass


# Main, handles initialisation and manages threads.
def main():
    print(__name__)

    # Initialising socket
    print("Initialising socket")
    global s, port
    s.bind(('0.0.0.0', port))

    # Find ip
    global ip
    ip = socket.gethostbyname(socket.gethostname())
    print("IP: " + ip)

    # Find subnet
    global subnet
    subnet = get_subnet(ip)

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
    s.sendto(new_enc(ext_type, socket.gethostname()), (controller_ip, port))

    # Scan for devices on network and send information to controller
    ext_devs = find_devices(ip, "endpoint")

    for dev in ext_devs:
        print("Requesting name from: " + dev)

        # Request dev for its name
        s.sendto(tlv_enc("who", "router"), (dev, port))

        # Wait for response
        who_is = ""
        while who_is == "":
            who_data, who_add = s.recvfrom(buff_size)
            who_is = tlv_dec(who_data).get("who")
            print(who_is)

        connections[who_is] = dev

    ext_devs = find_devices(ip, "router")

    for dev in ext_devs:
        s.sendto(dev, (controller_ip, port))

    # Launch packet reception thread
    rec_packets = RecPackets()
    rec_packets.start()

    # Launch packet sending thread
    send_packets = SendPackets()
    send_packets.start()


# Run main if script run at top level
if __name__ == "__main__":
    main()
