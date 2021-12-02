# Simple utility functions used by various components
# Author: Lydia MacBride

import socket


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ GENERAL PURPOSE ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Device hostname prefixes
PREFIXES = {
    "endpoint": "a2-endpoint",
    "router": "a2-router",
    "controller": "a2-controller"
}


# Get subnet
def get_subnet(ip):
    ip_split = ip.split(".")
    return ip_split[0] + "." + ip_split[1] + "." + ip_split[2]


# Print Debug
# Print string only when debug is True
def print_d(debug, string):
    if debug:
        print(string)


# Network device finder with different subnets
# Returns list of connected devices encoded and ready to send to controller
# Kind of hacky but designed to get around devices being connected to multiple docker networks
# TODO: Append all found devices
def find_devices(ip, dev_type, count=9):
    out = list()

    i = 0
    while i <= count:
        try:
            name = PREFIXES.get(dev_type) + str(i)
            print("Checking: " + name)
            dev_ip = socket.gethostbyname(name)
            print("Device found at: " + str(dev_ip))

            # Check if this is the searching device's ip
            print("Matching ip: " + str(ip == dev_ip))
            if ip != dev_ip:

                if dev_type == "router":
                    out.append(found_dev_enc(name, dev_ip))
                else:
                    out.append(name)

        except socket.gaierror:
            print("No device found")

        i += 1

    if len(out) > 0:
        print(out)

    return out


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ TLV ENCODING ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TLV Types dictionary
# Any packet with a type that isn't handled will be assigned type "unknown"
TLV_TYPES = {
    0: "who",
    1: "new",
    2: "exit",
    3: "name",
    4: "recipient",
    5: "string",
    6: "route",
    7: "combination",
    8: "unknown"
}


# Search dictionary for key corresponding to given value
# ASSUMES: all values in given dictionary are unique, otherwise will only return first occurrence
def val_to_key(value, d):
    try:
        return [key for key, val in d.items() if val == value][0]
    except (KeyError, IndexError):
        return 10


# TLV encoding
# TODO: Generalise similar cases
# Types:
def tlv_enc(tlv_type, data):
    type_num = val_to_key(tlv_type, TLV_TYPES)

    # Integer based data types
    if tlv_type == "exit":
        data_len = 0
        return type_num.to_bytes(1, 'big') + data_len.to_bytes(2, 'big')

    # String based data types
    # Name, String
    if tlv_type in ["who", "new", "name", "recipient", "string", "route"]:
        data_enc = str(data).encode("utf-8")
        return type_num.to_bytes(1, 'big') + len(data_enc).to_bytes(2, 'big') + data_enc

    # Combination
    if tlv_type == "combination":
        data_enc = data[0] + data[1]
        return type_num.to_bytes(1, 'big') + len(data_enc).to_bytes(2, 'big') + data_enc

    # Unknown packet types
    else:
        data_enc = str(data).encode("utf-8")
        return type_num.to_bytes(1, 'big') + len(data_enc).to_bytes(2, 'big') + data_enc


# TLV decoding
# TODO: Generalise similar cases
def tlv_dec(packet):
    tlv_type = packet[0]
    type_val = TLV_TYPES.get(tlv_type)
    ret_dict = dict()

    # Exit
    if type_val == "exit":
        ret_dict.update({type_val: 0})

    # Name, String, Unknown
    if type_val in ["who", "new", "name", "recipient", "string", "route", "unknown"]:
        ret_dict.update({type_val: packet[3:].decode("utf-8")})

    # Combination
    if type_val == "combination":
        p1_len = int.from_bytes(packet[4:6], 'big')

        ret_dict.update(tlv_dec(packet[3:6 + p1_len]))
        ret_dict.update(tlv_dec(packet[6 + p1_len:]))

    return ret_dict


# Message encoding
# TODO: Create more compact & generalised form
# Send using TLV format
def msg_enc(rec, name, string):
    # Encode recipient, name and string in tlv
    rec_tlv = tlv_enc("recipient", rec)
    name_tlv = tlv_enc("name", name)
    string_tlv = tlv_enc("string", string)

    # Encode all as combination packet and return
    return tlv_enc("combination", (rec_tlv, tlv_enc("combination", (name_tlv, string_tlv))))


# New Device encoding
def new_enc(dev_type, name):
    # Encode type and name in tlv
    new_tlv = tlv_enc("new", dev_type)
    name_tlv = tlv_enc("name", name)

    # Encode both as combination packet and return
    return tlv_enc("combination", (new_tlv, name_tlv))


# Route request encoding
# TODO: Revise this
def route_req_enc(name, rec):
    # Encode recipient and name
    name_tlv = tlv_enc("name", str(name))
    rec_tlv = tlv_enc("recipient", str(rec))

    # Encode both as combination packet and return
    return tlv_enc("combination", (name_tlv, rec_tlv))


# Found device packet
def found_dev_enc(name, route):
    # Encode name and route
    name_tlv = tlv_enc("name", name)
    route_tlv = tlv_enc("route", route)

    # Encode both as combination packet and return
    return tlv_enc("combination", (name_tlv, route_tlv))


"""
Shnámh mé san uisce gorm,
Go mall, ro mall.
Ach níor cheap mé faoin am.

Braithim uaim go mór an trá.
"""
