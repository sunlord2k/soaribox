import socket
import re

UDP_IP = "127.0.0.1"
UDP_PORT = 4353
MESSAGE = "This is a Test!"
TESTMESSAGE = "$SOARIM,SoariBox is going to Shutdown in 3 Seconds*"


def chksum_nmea(sentence):

    # This is a string, will need to convert it to hex for
    # proper comparsion below

    # String slicing: Grabs all the characters
    # between '$' and '*' and nukes any lingering
    # newline or CRLF
    chksumdata = re.sub("(\n|\r\n)","", sentence[sentence.find("$")+1:sentence.find("*")])

    # Initializing our first XOR value
    csum = 0

    # For each char in chksumdata, XOR against the previous
    # XOR'd char.  The final XOR of the last char will be our
    # checksum to verify against the checksum we sliced off
    # the NMEA sentence

    for c in chksumdata:
        # XOR'ing value of csum against the next char in line
        # and storing the new XOR value in csum
        csum ^= ord(c)

    # Do we have a validated sentence?
    print(hex(csum))
    return csum.to_bytes(1, "big").hex()


def send_udp(message, UDP_IP, UDP_PORT):
    message = "$SOARIM," + message + "*"
    check = chksum_nmea(message)
    print(check)
    message = bytes(message, 'utf-8') + bytes(check, 'utf-8') + b"\n"
    print(message)
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.sendto(message, (UDP_IP, UDP_PORT))


if __name__ == '__main__':
    print("UDP target IP: %s" % UDP_IP)
    print("UDP target port: %s" % UDP_PORT)
    print("message: %s" % MESSAGE)
    send_udp(MESSAGE, UDP_IP, UDP_PORT)
