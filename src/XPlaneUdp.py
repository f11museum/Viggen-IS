import socket
import struct
import binascii
import time


LISTEN_PORT = 49006
SEND_PORT = 49000

current_milli_time = lambda: int(round(time.time() * 1000))

class XPlaneUdp:

    def __init__(self, ip, port, listen_port=49006):
        self.xip = ip
        self.xport = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(0)
        self.sock.bind(("", listen_port))
        self.sendList = []
        self.dataList = {}
        self.lastDataTimer = current_milli_time()
        self.connected = False

    def readData(self):
        if (self.lastDataTimer+10000 < current_milli_time()):
            if (self.connected == False):
                print("reconnect")
                self.sendList = []
                self.dataList = {}
        while(True):
            try:
                data, addr = self.sock.recvfrom(1024)
                # print("received data:")
                # print(addr)
                # print(data)
                header=data[0:5]
                if(header==b"RREF,"):
                    self.lastDataTimer = current_milli_time()
                    self.connected = True
                    values =data[5:]
                    lenvalue = 8
                    numvalues = int(len(values)/lenvalue)
                    for i in range(0,numvalues):
                        singledata = data[(5+lenvalue*i):(5+lenvalue*(i+1))]
                        (idx,value) = struct.unpack("if", singledata)
                        #print("found values", idx, value)
                        if idx<len(self.sendList):
                            if self.sendList[idx] in self.dataList:
                                self.dataList[self.sendList[idx]] = value
                                #print("set ",self.sendList[idx], "value", value )
            except:
                #print('no data')
                break


    def sendDataref(self, dataref, value):
        message = b'DREF0'
        message = message + struct.pack("f", float(value))
        bytestring = dataref.encode()
        message = message + bytestring + b'\00'
        #print(message)

        for i in range(509):
            message = message+b'\x20'

        message = message[:509]

        self.sock.sendto(message, (self.xip, self.xport))

    def sendCommand(self, dataref):
        message = b'CMND0'

        bytestring = dataref.encode()
        message = message + bytestring + b'\00'
        #print(message)

        for i in range(509):
            message = message+b'\x20'

        message = message[:509]

        self.sock.sendto(message, (self.xip, self.xport))

    def getDataref(self, dataref, interval):
        if dataref not in self.dataList:
            self.createDataref(dataref, interval)
            return 0
        else:
            return self.dataList[dataref]

    def createDataref(self, dataref, interval):
        self.sendList.append(dataref)
        self.dataList[dataref] = 0
        index = len(self.sendList) - 1
        #print("createDataref ", index)
        message = b'RREF0'
        message = message + struct.pack("i", interval)
        message = message + struct.pack("i", index)
        bytestring = dataref.encode()
        message = message + bytestring + b'\00'
        cmd = b"RREF\x00"
        message = struct.pack("<5sii400s", cmd, interval, index, bytestring)
        assert(len(message)==413)
        #print(message[:50])
        self.sock.sendto(message, (self.xip, self.xport))

    def flush(self):
        """Drain any pending UDP packets from the socket buffer.

        Call this before (re)subscribing so old RREF, packets left over from a
        previous run are not mistakenly mapped onto our fresh sendList indices.
        """
        while True:
            try:
                self.sock.recvfrom(1024)
            except BlockingIOError:
                break
            except Exception:
                break

    def stopAllSubscriptions(self, max_index=512, rounds=3):
        """Tell X-Plane to stop streaming any dataref indices it may still have
        assigned to our IP:port from a previous run of this program.

        X-Plane's UDP is connectionless and has no global "reset" command. The
        only way to cancel a stream is to send RREF with interval=0 and the same
        index X-Plane assigned. Since a fresh Python process does not know the
        old indices, we cancel every index in range(0, max_index) for our own
        source port. Unsubscribed indices are simply ignored by X-Plane.

        The cancel is sent multiple times (rounds) because UDP is unreliable and
        we want X-Plane to actually process the cancellations before new
        subscriptions are created.

        This only affects X-Plane's subscription table for our listen port
        (49006 / 49007). Other programs using different ports are untouched.
        """
        cmd = b"RREF\x00"
        empty = b""
        for _ in range(rounds):
            for i in range(max_index):
                message = struct.pack("<5sii400s", cmd, 0, i, empty)
                self.sock.sendto(message, (self.xip, self.xport))
            time.sleep(0.01)

        # reset our own bookkeeping so a fresh subscription starts clean
        self.sendList = []
        self.dataList = {}
        self.connected = False
