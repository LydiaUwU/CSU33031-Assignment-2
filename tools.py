# Simple utility functions used by various components
# Author: Lydia MacBride

# Print Debug
# Print string only when debug is True
def print_d(debug, string):
    if debug:
        print(string)


# TLV encoding
# Types:
# - 0: Name
# - 1: String
# - 9: Combination
# TODO: Expand to contain network routing types
def tlv_enc(tlv_type, data):
    # Type 0: Name, Type 1: String
    if tlv_type == 0 or tlv_type == 1:
        data_enc = data.encode("utf-8")
        return tlv_type.to_bytes(1, 'big') + len(data_enc).to_bytes(2, 'big') + data_enc

    # Type 9: Combination
    elif tlv_type == 9:
        data_enc = data[0] + data[1]
        return tlv_type.to_bytes(1, 'big') + len(data_enc).to_bytes(2, 'big') + data_enc


# TLV decoding
def tlv_dec(packet):
    tlv_type = packet[0]

    # Type 0: Name, Type 1: String
    if tlv_type == 0 or tlv_type == 1:
        return packet[3:].decode("utf-8")

    # Type 9: Combination
    if tlv_type == 9:
        p1_len = int.from_bytes(packet[4:6], 'big')

        p1 = tlv_dec(packet[3:6 + p1_len])
        p2 = tlv_dec(packet[6 + p1_len:])

        return p1, p2


# Message encoding
# Send using TLV format
def msg_enc(name, string):
    # Encode name and string in tlv
    name_tlv = tlv_enc(0, name)
    string_tlv = tlv_enc(1, string)

    # Encode both as combination packet and return
    return tlv_enc(9, (name_tlv, string_tlv))
