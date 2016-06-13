#
# TCP Server
#

from socket import *
import binascii

# CRC-32 checksum function
"""def checksum(msg):
    poly = 0x04C11DB7           #poly defined for CRC32 on web
    for i in len(msg) -1:
        msg += '\x00\x00'   # padding with zeros
        print("Msg is now ", msg)
    print(msg, " is having a CRC checksum ")
    s = 0
    # loop taking 2 characters at a time
    for i in range(0, len(msg) - 2, 1):
        print("i is: ", i)
        w = (ord(msg[i]) << 8) + (ord(msg[i+1]))
        s += w
        print("s is ", s)
    print("S in binary)", bin(s))
    n = ~s
    print("Inverted value in binary")
    s = (s>>16) + (n>>16)
    print("ORed value in binary:", bin(s))
    s+=1
    print("s in bin: ", bin(s))
    return s"""

def calc_checksum(data):
    result=""
    crc = binascii.crc32(data)&0xFFFFFFFF
    for i in range(8):
        b = (crc >> (8*i)) & 0xFF
        print("b is ", b)
        result += ('%02X\n' % b)
    return result                     # this is the checksum for the frame


"""def checkCRC(message):
    #CRC-16-CITT poly, the CRC sheme used by ymodem protocol
    poly = 0x11021
    #16bit operation register, initialized to zeros
    reg = 0xFFFF
    #pad the end of the message with the size of the poly
    message += '\x00\x00'
    #for each bit in the message
    for byte in message:
        mask = 0x80
        while(mask > 0):
            #left shift by one
            reg<<=1
            #input the next bit from the message into the right hand side of the op reg
            if ord(byte) & mask:
                reg += 1
            mask>>=1
            #if a one popped out the left of the reg, xor reg w/poly
            if reg > 0xffff:
                #eliminate any one that popped out the left
                reg &= 0xffff
                #xor with the poly, this is the remainder
                reg ^= poly
    return reg"""

ack = bytes('1', 'UTF-8')
nack = bytes('0', 'UTF-8')


# ------- set up our sockets ------- #
buf = 1024                                          # buffering size
serverPort = 12000
HOST = ''
try:
    serverSocket = socket(AF_INET, SOCK_STREAM)
except socket.error:
    print("Failed to create socket")
    exit(2)
print("Socket created successfully")
serverSocket.bind((HOST, 12000))
serverSocket.listen(1)                                      # starts listening - sets maximum accept rate to 1
print('The server is ready to receive')

file = open("outputdata.txt", "wb")                         # open file for writing

# ---- deal with received data ---- #
connectionSocket, addr = serverSocket.accept()
print("Connection successful")                              # connected to client
while 1:                                                    # loop forever
    data = connectionSocket.recv(buf)                       # buffered data size is up to 512 bytes
    # this will have the header, trailer, etc in it
    # after 3 bytes/24 bits (flag, src_Addr and dest_Addr), we have the data
    # we have to store this data
    # read in the entire frame
    # then split it up
    # packet = flag + addresses + control + protocol + paylod + checksum + flag
    print("Received some data!")
    chk = CRC32(data)
    print("Checksum function returned: ", chk)              # get the checksum
    # should now have "if chk == data.checksum_Field, i.e. the two checksums match
    if chk == 0:
        print("Received from client:", str(data))
        connectionSocket.send(ack)
        print("Sent the ack frame back to the client")
        file.write(data)                                    # write the data to the file once we know received correctly
    else:
        print("Did not receive correct info from client - sent back a nack frame")
        connectionSocket.send(nack)                         # NACK
    data = ""                                               # reset and continue listening for next packet

# only close the socket when we fall out of the loop
file.close()                                                # finished writing to file
connectionSocket.close()


# parse the header - first X bytes
def parse_header(inputdata):
    ack_bit = inputdata.split("x")



# need to implement a gremlin function