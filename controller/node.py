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
# Greets: Emmet! For helping me debug this
def find_route(src, dst):
    route = find_route_rec(src, dst, [src])

    if route is None:
        print("No route found")
        return None

    while len(route) > 0:
        node = route[0]

        if len(route) <= 1:
            print("Destination reached: " + str(dst.address))
            node.routes.update({dst.address: dst.address})
        else:
            print("Updating node: " + str(node.address[0]) + ", " + str(route[1].address[0]))
            node.routes.update({dst.address: route[1]})

        print(node.routes)

        route.remove(node)

    return route


# Recursive helper function for find route
# TODO: Return shortest route, currently returns last found route
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

            # Check that node has unsearched connections before recurring
            if len([e for e in node.connections if e not in route]) != 0:
                return find_route_rec(node, dst, route)


# TODO: Remove this, it's test code
if __name__ == "__main__":
    cooper = Node(("coop", ""), "", "Cooper")
    dougie = Node(("doug", ""), "", "Dougie")
    harry = Node(("harr", ""), "", "Harry")
    lucy = Node(("lucy", ""), "", "Lucy")
    hawk = Node(("hawk", ""), "", "Hawk")
    gordon = Node(("gord", ""), "", "Gordon")
    philip = Node(("phil", ""), "", "Philip")

    r0 = Node(("r0", ""), "", "R0")
    r1 = Node(("r1", ""), "", "R1")
    r2 = Node(("r2", ""), "", "R2")
    r3 = Node(("r3", ""), "", "R3")
    r4 = Node(("r4", ""), "", "R4")

    cooper.connect(dougie)
    cooper.connect(r0)
    harry.connect(r2)
    lucy.connect(r1)
    hawk.connect(r3)
    hawk.connect(r4)
    gordon.connect(r4)
    r0.connect(r1)
    r1.connect(r2)
    r1.connect(r3)
    r2.connect(r3)
    r3.connect(r4)

    route_test = find_route(harry, cooper)
