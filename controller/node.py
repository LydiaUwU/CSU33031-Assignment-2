# Network node class and methods
# Author: Lydia MacBride


"""
~~~~ Routing table format ~~~~
(╯°□°）╯︵ ┻━┻

Each node in a network contains node.routes, which is a dictionary of routes by destination.
These dictionary follow this format:
{
    <DESTINATION_IP>: <NEXT_NODE_IN_ROUTE>
}
"""


# Node class
class Node:
    # Constructor
    def __init__(self, address, dev_type, name=None):
        self.name = name
        self.address = address
        self.type = dev_type
        self.connections = list()  # List of all connected nodes
        self.routes = dict()  # Contains a list of dictionaries with routing

    # Connect another node to this one
    def connect(self, node, bi=True):
        if node not in self.connections:
            self.connections.append(node)

        # Add self to node's connections
        if bi:
            node.connect(self, False)

    pass


# Find route between source and destination
# Updates all nodes in route's routing table with discovered route and returns the route
def find_route(src, dst):
    route = find_route_rec(src, dst, list())

    for node in route:
        print("Updating node: " + str(node.address[0]))
        node.routes.update({dst.address: route[0]})

        print(node.routes)

        route.remove(node)

    return route


# Recursive helper function for find route
# TODO: Find way to return multiple routes if found, currently inefficient and brute force
def find_route_rec(src, dst, route):
    print("src: " + str(src.address[0]) + ", dst: " + str(dst.address[0]))
    for node in src.connections:
        print("Checking: " + str(node.address[0]))

        if node.address == dst.address:
            print("Destination found: " + str(node.address[0]))
            route.append(node)
            for i in route:
                print(str(i.address[0]) + "\n")
            return route
        elif node not in route:
            print("Destination not found")
            route.append(node)
            for i in route:
                print(str(i.address[0]) + "\n")
            return find_route_rec(node, dst, route)


# TODO: Remove this, it's test code
if __name__ == "__main__":
    a = Node(("0.0.0.0", "0000"), "test", "A")
    b = Node(("0.0.0.1", "0000"), "test", "B")
    c = Node(("0.0.0.2", "0000"), "test", "C")
    a.connect(b)
    b.connect(c)
    r = find_route(a, c)
