# Simple messaging application
# Author: Lydia MacBride

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
            msg = tlv_dec(data)
            timestamp = time.strftime('%H:%M:%S')
            incoming.append((msg.get("name"), msg.get("string"), timestamp))

    pass


# Message Sending thread
# TODO: Generalise this
class SendMessages(threading.Thread):
    def run(self):
        print("Message sending thread starting")

        while running:
            for msg in outgoing:
                print_d(debug, "Sending the message \"" + msg[1] + "\" to " + msg[0])

                global s, loc_port
                s.sendto(msg_enc(msg[0], msg[1]), ('localhost', loc_port))

                outgoing.remove(msg)

            time.sleep(1.0)

    pass


# TODO: User input thread
class ProcInput(threading.Thread):
    def run(self):
        print("User input thread starting")

        # Bring global variables into scope
        global name
        global debug
        global running

        while running:
            # Set prompt to 💌 when there is unread messages
            prompt = "✨" if len(incoming) == 0 else "💌"
            user_in = input("\n" + prompt + "〉")

            # Send <msg>
            # TODO: Add recipient parameter
            # TODO: Character limit of 2 bytes
            if user_in[0:4] == "send":
                outgoing.append((name, user_in[5:]))

            # ls TODO: -a
            elif user_in[0:2] == "ls":
                for msg in incoming:
                    # TODO: Print message reception time
                    print(msg[3] + " | " + msg[0] + ": " + msg[1])
                    incoming.remove(msg)

                    # TODO: Store removed messages in file

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
                print("send <msg>       Send a message\n"
                      "ls (-a)          List unread messages (-a to list all messages)\n"
                      "debug            Toggle debug output\n" 
                      "exit             Stop and exit application\n"
                      "help             List available commands")

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
            print("Stopping threads")

            # Send shutdown signal to service
            exit_pck = tlv_enc("exit", 0)
            s.sendto(exit_pck, ("localhost", loc_port))

            # Stop threads
            send_messages.join()
            proc_input.join()

            # Send exit packet to close packet reception
            s.sendto(exit_pck, ("localhost", app_port))

            rec_messages.join()

            break

    print("Application shutdown successful!")


# For debug purposes, run main if script run at top level
if __name__ == "__main__":
    # Get username
    name_main = input("Enter your name: ")
    print("Your name is: " + name_main)

    main(name_main)
