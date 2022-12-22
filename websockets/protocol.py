"""
Websockets protocol
"""

import re
import struct
import random
from collections import namedtuple

try:
    const(0x0)
except NameError:
    def const(x):
        return x

# Opcodes
OP_CONT = const(0x0)
OP_TEXT = const(0x1)
OP_BYTES = const(0x2)
OP_CLOSE = const(0x8)
OP_PING = const(0x9)
OP_PONG = const(0xa)

# Close codes
CLOSE_OK = const(1000)
CLOSE_GOING_AWAY = const(1001)
CLOSE_PROTOCOL_ERROR = const(1002)
CLOSE_DATA_NOT_SUPPORTED = const(1003)
CLOSE_BAD_DATA = const(1007)
CLOSE_POLICY_VIOLATION = const(1008)
CLOSE_TOO_BIG = const(1009)  # send this when running out of memory in read_fraome
CLOSE_MISSING_EXTN = const(1010)
CLOSE_BAD_CONDITION = const(1011)


URL_RE = re.compile(r'(ws[s]?)://([A-Za-z0-9\-\.]+)(?:\:([0-9]+))?(/.+)?')
URI = namedtuple('URI', ('proto', 'hostname', 'port', 'path'))


def urlparse(uri):
    """Parse ws:// URLs"""
    match = URL_RE.match(uri)
    if match:
        proto, host, port, path = (match.group(1),
                                   match.group(2),
                                   match.group(3),
                                   match.group(4))
        if port is None:
            port = 80

        return URI(proto, host, int(port), path)


class Websocket():
    is_client = False

    def __init__(self, stream):
        self._stream = stream
        self.open = True
        self.fragment = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def __aiter__(self):
        return self

    async def __anext__(self):
        while self.open:
            value = await self.recv()
            if value:
                return value
        raise StopAsyncIteration

    def settimeout(self, timeout):
        pass
        # self._sock.settimeout(timeout)

    async def read_frame(self, max_size=None):
        # Frame header
        byte1, byte2 = struct.unpack('!BB', await self._stream.readexactly(2))

        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        fin = bool(byte1 & 0x80)
        opcode = byte1 & 0x0f

        # Byte 2: MASK(1) LENGTH(7)
        mask = bool(byte2 & (1 << 7))
        length = byte2 & 0x7f

        if length == 126:  # Magic number, length header is 2 bytes
            length, = struct.unpack('!H', await self._stream.readexactly(2))
        elif length == 127:  # Magic number, length header is 8 bytes
            length, = struct.unpack('!Q', await self._stream.readexactly(8))

        if mask:  # Mask is 4 bytes
            mask_bits = await self._stream.readexactly(4)

        try:
            data = await self._stream.readexactly(length)
        except MemoryError:
            # We can't receive this many bytes, close the socket
            self.close(code=CLOSE_TOO_BIG)
            await self._stream.drain()
            return True, OP_CLOSE, None

        if mask:
            data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))

        return fin, opcode, data

    def write_frame(self, opcode, data=b''):
        fin = True
        mask = self.is_client  # messages sent by client are masked

        length = len(data)

        # Frame header
        # Byte 1: FIN(1) _(1) _(1) _(1) OPCODE(4)
        byte1 = 0x80 if fin else 0
        byte1 |= opcode

        # Byte 2: MASK(1) LENGTH(7)
        byte2 = 0x80 if mask else 0

        if length < 126:  # 126 is magic value to use 2-byte length header
            byte2 |= length
            self._stream.write(struct.pack('!BB', byte1, byte2))

        elif length < (1 << 16):  # Length fits in 2-bytes
            byte2 |= 126  # Magic code
            self._stream.write(struct.pack('!BBH', byte1, byte2, length))

        elif length < (1 << 64):
            byte2 |= 127  # Magic code
            self._stream.write(struct.pack('!BBQ', byte1, byte2, length))

        else:
            raise ValueError()

        if mask:  # Mask is 4 bytes
            mask_bits = struct.pack('!I', random.getrandbits(32))
            self._stream.write(mask_bits)
            data = bytes(b ^ mask_bits[i % 4] for i, b in enumerate(data))

        self._stream.write(data)

    async def recv(self):
        popcode = None # previos op code
        buf = bytearray(0)

        while self.open:
            try:
                fin, opcode, data = await self.read_frame()
                # print("f: {}\no: {}\nd: {}".format(fin, opcode, data))
            except (ValueError, EOFError):
                self._close()
                return

            # if it's a continuation frame, it's the same data-type
            if opcode == OP_CONT:
                opcode = popcode
            else:
                buf = bytearray(0)
                popcode = opcode

            if opcode == OP_TEXT or opcode == OP_BYTES:
                buf += data

            elif opcode == OP_CLOSE:
                self.close()
                await self.wait_closed()
                return

            elif opcode == OP_PONG:
                # Ignore this frame, keep waiting for a data frame
                # note that we are still connected, yah?
                # if we dont get a pong, we aren't connected.
                continue

            elif opcode == OP_PING:
                # We need to send a pong frame
                self.write_frame(OP_PONG, data)
                await self._stream.drain()
                continue

            else:
                # unknown opcode
                raise ValueError(opcode)

            if fin:
                # gonna leak a bit since im not clearing the buffer on exit.
                if opcode == OP_TEXT:
                    return buf.decode('utf-8')
                elif opcode == OP_BYTES:
                    return buf

    async def send(self, buf):
        if not self.open:
            return

        if isinstance(buf, str):
            opcode = OP_TEXT
            buf = buf.encode('utf-8')
        elif isinstance(buf, bytes):
            opcode = OP_BYTES
        else:
            raise TypeError()

        self.write_frame(opcode, buf)
        await self._stream.drain()

    async def wait_closed(self):
        # drain stream to send off any final frames
        # close the stream (and underlying connection)
        await self._stream.drain()
        await self._stream.wait_closed()

    def close(self, code=CLOSE_OK, reason=''):
        '''Close the websocket.  Must call await websocket.wait_closed after'''
        if not self.open:
            return

        buf = struct.pack('!H', code) + reason.encode('utf-8')

        self.write_frame(OP_CLOSE, buf)
        self._close()

    def _close(self):
        self.open = False
