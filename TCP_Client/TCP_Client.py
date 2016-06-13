#
# TCP Client
#
from socket import *
import os, sys
from struct import *
import binascii
from binascii import hexlify

# DEFINE THE SOCKETS
serverName = 'localhost'
serverPort = 12000
try:
    clientSocket = socket(AF_INET, SOCK_STREAM)
except socket.error:
    print("Failed to create socket")
    exit(2)
print("Socket created successfully")
clientSocket.connect((serverName, serverPort))
print("Connection established to server")

# -------Functions used--------
def chunks(my_data, n):                               # breaks all the data into chunks of size n
    for i in range(0, len(my_data), n):
        yield my_data[i:i+n]

def calc_checksum(data):
    g_poly = 0x04C11DB7 # defined on web fro CRC32
    result=""
    crc = binascii.crc32(data)&0xFFFFFFFF
    for i in range(8):
        b = (crc >> (8*i)) & 0xFF
        print("b is ", b)
        result += ('%02X\n' % b)
    return result


# -- have to find some way of encapsulating the chunks in a dataframe with correct structure --
"""header=""
trailer = ""
data = "" # 8 bytes at a time = 64 bits

flag = 0x7E                                      # 01111110 binary, the flag to indicate the start of the frame
# used for both opening and closing flags
control = 0x0000 # 16 bits
CRC = 0x00000000 # 32 bits
#packet = flag + control + src_addr + dest_addr + data + CRC + flag  # this is the flag"""

src_addr = hexlify(getaddrinfo(clientSocket))    # 16 bits - 2 bytes
dest_addr = 0x2EE0 # 16 bits - 2 bytes                                # now length 3 bytes
flag = 0x7E # 1 byte : indicates start of frame                     # now length 5 bytes
header = flag # header should be 64 bits long (16 bytes)
trailer = ""

file = open("data.txt", "rb")                         # open for reading and writing
data = file.read(3360)
fileremaining = len(data)                             # how much data in file left to send - counter
seq = 0                                               # seq num of the frame
ack_seq = 0                                           # ack seq num
ack=False

while fileremaining > 0:                              # while we still have something to send
    for chunk in chunks(data, 8):                     # 8 bytes at a time of input data
        fileremaining -= len(chunk)
                                        # now we should be packaging it into a dataframe of particular length - the "chunk" is the payload for the frame
                                        # packet = flag + control + src_addr + dest_addr + chunk + CRC + flag
                                        # clientSocket.send(packet)
        chk = calc_checksum(chunk)
        trailer += chk + flag           # now we have a trailer containing the checksum value
        header = flag + seq + src_addr + dest_addr
        print("Checksum: ", chk)        # when the server does a checksum on this chunk, should yield same result - send ack
        packet = header + chunk + trailer
        clientSocket.send(packet)
        print("Waiting for acknowledgement from the server..")
        while ack != True:
            acknowledgement = clientSocket.recv(16) # read in the ack frame fro the server for next while iteration
            clientSocket.settimeout(10)
            if bytes('1', 'UTF-8') in acknowledgement:             # read in the returned data from the server - should be an ack
                ack = True                                # w# e can come out of loop to move onto the next chunk
                print("Received ACK frame from server - packet ", seq, " sent successfully.")
            elif bytes('0', 'UTF-8') in acknowledgement:           # we received a nack frame - the packet had been corrupted
                clientSocket.send(chunk)                # resend the packet
                print("Just resent the packet with seq num ", seq)
        seq += 1                                        # we are on to the next chunk
        ack = False
        ack_seq += 1                                    # the next ack has a different seq num
print("Stopped generating frames - end of file")
# only fall out of this loop if the amount of file remaining is 0

print("Sending completed")
file.close()
clientSocket.close()


"""
CLIENT SHOULD:
    >read data from input file created              # done
    >create frames with header and trailer and data (8 bytes), making use of bit stuffing
    >calculate checksum and store in trailer
    >applies gremlin function to corrupt/drop the packet if needed
    >Continuous RQ mode

Server should:
    >Check the checksum
    >return acks and nacks                          # done
    >write the frame to an output file              # done

The basic idea of CRC algorithms is simply to treat the message as an
enormous binary number, to divide it by another fixed binary number,
and to make the remainder from this division the checksum. Upon
receipt of the message, the receiver can perform the same division and
compare the remainder with the "checksum" (transmitted remainder).



    """