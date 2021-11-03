# Simple messaging application
# Author: Lydia MacBride
# TODO: Change packet encoding from utf-8

import socket
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


# Message Reception
# TODO: Might need to convert this to a function run in main()
class RecMessages(threading.Thread):
    def run(self):
        print("Message reception thread starting")

        while running:
            global s, incoming
            data, address = s.recvfrom(buff_size)
            msg = data.decode("utf-8")
            timestamp = time.strftime('%H:%M:%S')
            incoming.append((msg[0], msg[1], timestamp, False))


# TODO: Message Sending thread
class SendMessages(threading.Thread):
    def run(self):
        print("Message sending thread starting")

        while running:
            time.sleep(1.0)

            for msg in outgoing:
                print_d(debug, "Sending the message \"" + msg[1] + "\" to " + msg[0])

                global s, loc_port
                s.sendto(msg_enc(msg[0], msg[1]), ('localhost', loc_port))


# TODO: User input thread
class ProcInput(threading.Thread):
    def run(self):
        print("User input thread starting")

        global running
        while running:
            user_in = input("\n✨〉")

            # Send <msg>
            # TODO: Add recipient parameter
            # TODO: Character limit of 16 bytes
            if user_in[0:4] == "send":
                global name
                outgoing.append((name, user_in[4:]))

            # Test
            if user_in == "test":
                global name
                outgoing.append((name, "SERVICE TEST"))

            # TODO: ls -a
            # TODO: List only unread messages by default
            elif user_in[0:2] == "ls":
                for msg in incoming:
                    # TODO: Print message reception time
                    print(msg[3] + "|" + msg[0] + ": " + msg[1])

            # debug
            elif user_in == "debug":
                global debug
                debug = not debug
                print("Debug output " + "enabled" if debug else "disabled")

            # exit
            elif user_in == "exit":
                print("Shutting down")
                running = False

            # TODO: help
            elif user_in == "help":
                print("HELP")

            # Invalid input
            else:
                print("Invalid input. Run help to see available commands")

    pass


# Main function, will handle launching and managing various threads
def main():
    print(__name__)

    # Initialising socket
    print("Initialising socket")
    global app_port
    s.bind(('localhost', app_port))

    # Request username
    global name
    name = input("Enter your name: ")
    print("Your name is: " + name)

    # Start message reception thread
    rec_messages = RecMessages()
    rec_messages.start()

    # Start message sending thread
    send_messages = SendMessages()
    send_messages.start()

    # Start user input thread
    proc_input = ProcInput()
    proc_input.start()

    # Rejoin threads when exit is run
    while True:
        if not running:
            # TODO: Send shutdown signal to service

            # Stop threads
            rec_messages.join()
            send_messages.join()
            proc_input.join()

            break

    print("Shut down complete!")


# For debug purposes, run main if script run at top level
if __name__ == "__main__":
    main()
