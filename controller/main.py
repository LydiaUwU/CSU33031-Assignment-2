# Network controller
# Handles device address assignment and providing routing infomation for devices with unknown recipient
# Author: Lydia MacBride
# Is aoibhinn liom mo mhná chéile

# TODO: Add debug output

import threading
from tools import *
from node import *


# Variables
port = 51510
buff_size = 4096
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
running = True

# Queues
outgoing = list()

# Node list
nodes = list()


# Packet reception thread
class RecPackets(threading.Thread):
    def run(self):
        print("Packet reception thread starting")

        global running, nodes
        while running:
            data, address = s.recvfrom(buff_size)
            pck = tlv_dec(data)

            # New device on network
            if "new" and "name" in pck:
                new_node = Node(address, pck.get("new"), pck.get("name"))

                # Connect to devices on same subnet
                for node in nodes:
                    if get_subnet(node.address[0]) == get_subnet(address[0]):
                        node.connect(new_node)

                # Add node to nodes
                nodes.append(new_node)

            # Different subnet device found
            if "route" in pck:
                for i in nodes:
                    if i.address == address:
                        for j in nodes:
                            if j.address == pck.get("route"):
                                i.connect(j)

            # Routing information request
            if "name" and "recipient" in pck:
                name = pck.get("name")

                # Search for node by name, else use specified address
                rec = pck.get("recipient")

                if name != "None":
                    for node in nodes:
                        if node.name == name:
                            rec = node.address
                            break

                route = "None"

                for node in nodes:
                    if node.address == address:
                        # Check for pre-existing routing information
                        if node.routes.get(rec) is not None:
                            route = node.routes.get(rec)
                            break

                        # If route not found run find_route()
                        rec_node = Node(rec, None, name)
                        find_route(node, rec_node)

                        # Check again for routing information
                        if node.routes.get(rec) is not None:
                            route = node.routes.get(rec)

                        break

                # Return routing information
                outgoing.append((tlv_enc("route", route), address))

    pass


# Packet sending thread
class SendPackets(threading.Thread):
    def run(self):
        print("Packet sending thread starting")

        global running, s
        while running:
            for pck in outgoing:
                s.sendto(pck[0], pck[1])

                outgoing.remove(pck)

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
