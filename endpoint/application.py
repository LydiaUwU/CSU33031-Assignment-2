# Simple messaging application
# Author: Lydia MacBride

import threading
import time
from tools import *

# Variables
loc_port = 51511
app_port = 51512
buff_size = 4096
debug = False  # TODO: Make debug in scope of service.py
running = True
name = ""
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Queues
incoming = list()
outgoing = list()


# Packet Reception
# TODO: Generalise
class RecPackets(threading.Thread):
    def run(self):
        print("Message reception thread starting")

        global running, s, buff_size, incoming
        while running:
            data, address = s.recvfrom(buff_size)
            msg = tlv_dec(data)
            timestamp = time.strftime('%H:%M:%S')
            incoming.append((msg.get("name"), msg.get("string"), timestamp))

    pass


# Packet Sending thread
class SendPacket(threading.Thread):
    def run(self):
        print("Message sending thread starting")

        global running, s, loc_port
        while running:
            for pck in outgoing:

                s.sendto(pck, ('localhost', loc_port))

                outgoing.remove(pck)

    pass


# User input thread
class ProcInput(threading.Thread):
    def run(self):
        print("User input thread starting")

        # Bring global variables into scope
        global name, debug, running

        while running:
            # Set prompt to 💌 when there is unread messages
            prompt = "✨" if len(incoming) == 0 else "💌"
            user_in = input("\n" + prompt + "〉")

            # Send <msg>rec_messages
            # TODO: Character limit of 2 bytes
            if user_in[0:4] == "send":
                input_str = user_in.split(" ")

                # Check for invalid input
                if len(input_str) < 3:
                    print("Invalid input")
                    continue

                rec = input_str[1]
                msg = ' '.join(input_str[2:])

                print("Sending: " + msg)
                outgoing.append(msg_enc(rec, name, msg))

            # ls TODO: -a
            elif user_in[0:2] == "ls":
                for msg in incoming:
                    print(msg[2] + " | " + msg[0] + ": " + msg[1])
                    incoming.remove(msg)

                    # TODO: Store removed messages in file

            # ip
            elif user_in == "ip":
                print("Hostname: " + str(socket.gethostname()))
                print("IP: " + str(socket.gethostbyname(socket.gethostname())))

            # debug
            elif user_in == "debug":
                debug = not debug
                print("Debug output " + "enabled" if debug else "disabled")

            # exit
            elif user_in == "exit":
                print("Shutting down")
                running = False

            # help
            elif user_in == "help":
                print("send <user> <msg>    Send a message to a specified user\n"
                      "ls                   List unread messages\n"
                      "ip                   List endpoint's hostname and IP\n"
                      "debug                Toggle debug output\n" 
                      "exit                 Stop and exit application\n"
                      "help                 List available commands")

            # Invalid input
            else:
                print("Invalid input. Run help to see available commands")

    pass


# Main function, will handle launching and managing various threads
def main(name_in):
    print(__name__)

    # Initialising socket
    print("Initialising socket")
    global app_port
    s.bind(('localhost', app_port))

    # Load username from arguments
    global name
    name = name_in

    # Start message reception thread
    rec_packets = RecPackets()
    rec_packets.start()

    # Start message sending thread
    send_packets = SendPacket()
    send_packets.start()

    # Start user input thread
    proc_input = ProcInput()
    proc_input.start()

    # Rejoin threads when exit is run
    global running
    while True:
        if not running:
            print("Stopping threads")

            # Send shutdown signal to service
            exit_pck = tlv_enc("exit", 0)
            s.sendto(exit_pck, ("localhost", loc_port))

            # Stop threads
            send_packets.join()
            proc_input.join()

            # Send exit packet to close packet reception
            s.sendto(exit_pck, ("localhost", app_port))

            rec_packets.join()

            break

    print("Application shutdown successful!")


# For debug purposes, run main if script run at top level
if __name__ == "__main__":
    # Get username
    name_main = input("Enter your name: ")
    print("Your name is: " + name_main)

    main(name_main)
