# Simple utility functions used by various components
# Author: Lydia MacBride


# Constants
# TLV Types dictionary
# Any packet with a type that isn't handled will be assigned type "unknown"
TLV_TYPES = {
    0: "ack",
    1: "new",
    2: "exit",
    3: "name",
    4: "string",
    9: "combination",
    10: "unknown"
}


# Search dictionary for key corresponding to given value
# ASSUMES: all values in given dictionary are unique, otherwise will only return first occurrence
def val_to_key(value, d):
    try:
        return [key for key, val in d.items() if val == value][0]
    except (KeyError, IndexError):
        return 10


# Print Debug
# Print string only when debug is True
def print_d(debug, string):
    if debug:
        print(string)


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
    if tlv_type in ["new", "name", "string"]:
        data_enc = data.encode("utf-8")
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
    if type_val in ["new", "name", "string", "unknown"]:
        ret_dict.update({type_val: packet[3:].decode("utf-8")})

    # Combination
    if type_val == "combination":
        p1_len = int.from_bytes(packet[4:6], 'big')

        ret_dict.update(tlv_dec(packet[3:6 + p1_len]))
        ret_dict.update(tlv_dec(packet[6 + p1_len:]))

    return ret_dict


# Message encoding
# Send using TLV format
def msg_enc(name, string):
    # Encode name and string in tlv
    name_tlv = tlv_enc("name", name)
    string_tlv = tlv_enc("string", string)

    # Encode both as combination packet and return
    return tlv_enc("combination", (name_tlv, string_tlv))


# New Device encoding
def new_enc(type, name):
    # Encode type and name in tlv
    new_tlv = tlv_enc("new", type)
    name_tlv = tlv_enc("name", name)

    # Encode both as combination packet and return
    return tlv_enc("combination", (new_tlv, name_tlv))
