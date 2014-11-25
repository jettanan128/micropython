import pyb
import gc
import struct

import logging
import uasyncio.core as asyncio

from knxBaosFT12Header import KnxBaosFT12Header


# Service code for KNX EMI2
# Reset used for fixed frame telegrams transmitted in packets of length 1
EMI2_L_RESET_IND = 0xa0

# Standard KNX frame, inclusive bus monitor mode!
MAX_FRAME_LENGTH = 128  # max. length of KNX data frame

FT12_START_FIX_FRAME = 0x10  # start byte for frames with fixed length
FT12_START_VAR_FRAME = 0x68  # start byte for frames with variable length
FT12_CONTROL_SEND = 0x53  # control field for sending udata to module
FT12_CONTROL_RCV_MASK = 0xdf  # mask to check Control field for receiving
FT12_CONTROL_RCV = 0xd3  # control field for receiving udata to module
FT12_END_CHAR = 0x16  # the end character for FT1.2 protocol
FT12_FCB_MASK = 0x20  # mask to get fcb byte in control field
#FT12_LAST_SEND_FCB = m_nLastSendFcb  # the last frame count bit for sending
#FT12_NEXT_SEND_FCB = (m_nLastSendFcb ^= 0x20)  # the next frame count bit for sending
#FT12_LAST_RCV_FCB = m_nLastRcvFcb  # the last frame count bit for receiving
#FT12_NEXT_RCV_FCB = (m_nLastRcvFcb ^= 0x20)  # the next frame count bit for receiving
FT12_ACK = 0xe5  # acknowledge byte for FT1.2 protocol

# Control bytes for fixed length telegrams
FT12_RESET_IND = 0xc0  # reset indication
FT12_RESET_REQ = 0x40  # control field for sending a reset request to BAU
FT12_STATUS_REQ = 0x49  # status request
FT12_STATUS_RES = 0x8b  # respond status
FT12_CONFIRM_ACK = 0x80  # confirm acknowledge
FT12_CONFIRM_NACK = 0x81  # confirm not acknowledge


class TimeoutError(Exception):
    """
    """


class KnxBaosFT12:
    """
    """
    def __init__(self, tlsap, uartNum=2):
        """
        """
        self._tlsap = tlsap  # find a better name

        self._logger = logging.getLogger("KnxBaosFT12")

        self._uart = pyb.UART(uartNum)
        self._uart.init(19200, bits=8, parity=0, stop=1)

        self._lastSendFcb = 0x00
        self._lastRecvFcb = 0x00

    @property
    def _nextSendFcb(self):
        self._lastSendFcb ^= FT12_FCB_MASK
        return self._lastSendFcb

    @property
    def _nextRecvFcb(self):
        self._lastRecvFcb ^= FT12_FCB_MASK
        return self._lastRecvFcb

    @asyncio.coroutine
    def _transmitterLoop(self):
        """ Poll tlsap.getOutMessage() and send to uart

        Add header, checksum...

        Manage ack.

        manage wait?
        """
        while True:
            try:
                message = self._tlsap.getOutMessage()
                if message:
                    pass

                asyncio.sleep(10)

            except Exception as e:
                self._logger.debug("receiveLoop()")
                self._logger.debug(e)

    @asyncio.coroutine
    def _receiveLoop(self):
        """ Poll uart and send to tlsap.putInMessage()

        Decode frame, remove header, check validity (checksum)...

        Manage ack.
        """
        while True:
            try:

                # If data available, read complete telegram
                if self._uart.any():
                    telegram = []
                    while True:
                        c = self._uart.readchar()
                        telegram.append(c)
                        if telegram[-1] == FT12_END_CHAR:
                            break
                        #@todo: use timeout_char...

                    # Send ACK
                    self._uart.writechar(FT12_ACK)

                    self._logger.debug("receiveLoop(): data={}".format(repr(telegram)))

                    # Decode frame
                    controlField, message = self._decodeTelegram(telegram)

                    # Dispatch service
                    self._tlsap.putInMessage(message)

                asyncio.sleep(10)

            except Exception as e:
                self._logger.debug("receiveLoop()")
                self._logger.debug(e)

    def _decodeTelegram(self, telegram):
        """
        """
        header

    def start(self, loop):
        """ Start internal loops
        """
        loop.add_task(self._transmitterLoop())
        loop.add_task(self._receiveLoop())

    def resetDevice(self):
        """ Reset KnxBaos device
        """
        data = (FT12_START_FIX_FRAME, FT12_RESET_REQ, FT12_RESET_REQ, FT12_END_CHAR)
        self._logger.debug("reset(): send data={}".format(repr(data)))
        self._uart.write(data)
        pyb.delay(10)
        ack = self._uart.readchar()
        self._logger.debug("reset: received ack={}".format(hex(ack)))


    #def getParam(self, first, nb=1):

        ## send FT1.2 control field
        ##controlField = int('0b10011', 2)
        ##controlField |= 1 << 6
        ##controlField |= 1 << 7  # 1 = host (application) to BAOS module
                                ### 0 = BAOS module to hos (application)
                                ### Really???!!???
        #controlField = 0x53 + self._nextSendFcb

        ## Send BAOS message
        #main = '\xf0'
        #sub = '\x07'
        #message = main + sub + chr(first) + chr(nb)

        ## Send FT1.2 check sum
        #checkSum = controlField
        #for c in message:
            #checkSum += ord(c)
        #checkSum %= 0x100

        ## Send data
        #data = chr(FT12_START_VAR_FRAME) + chr(len(message)+1) + chr(len(message)+1) + chr(FT12_START_VAR_FRAME) + chr(controlField) + message + chr(checkSum) + chr(FT12_END_CHAR)
        #self._logger.debug("getParam: send data={}".format(repr(data)))
        #for c in data:
            #self._uart.writechar(ord(c))

        ## Wait for ack
        #pyb.delay(10)
        #if self._uart.any():
            #ack = self._uart.readchar()
            #self._logger.debug("getParam: received ack={}".format(hex(ack)))
        #else:
            #raise TimeoutError("timeout while reading acknowledge")

        ## Read answer
        #pyb.delay(50)
        #self.listen()

    #def getDatapoint(self, first, nb=1):
        ## send FT1.2 control field
        ##frameCountBit ^= 0x20          # which autmatically toggles at each call
        ##controlField |= 1 << 6
        ##controlField |= 1 << 7  # 1 = host (application) to BAOS module
                                ### 0 = BAOS module to hos (application)
                                ### Really???!!???
        #controlField = 0x53 + self._nextSendFcb

        ## Send BAOS message
        #main = '\xf0'
        #sub = '\x05'
        #message = main + sub + chr(first) + chr(nb)

        ## Send FT1.2 check sum
        #checkSum = controlField
        #for c in message:
            #checkSum += ord(c)
        #checkSum %= 0x100

        ## Send data
        #data = chr(FT12_START_VAR_FRAME) + chr(len(message)+1) + chr(len(message)+1) + chr(FT12_START_VAR_FRAME) + chr(controlField) + message + chr(checkSum) + chr(FT12_END_CHAR)
        #self._logger.debug("getDatapoint: send data={}".format(repr(data)))
        #for c in data:
            #self._uart.writechar(ord(c))

        ## Wait for ack
        #pyb.delay(10)
        #if self._uart.any():
            #ack = self._uart.readchar()
            #self._logger.debug("getDatapoint: received ack={}".format(hex(ack)))
        #else:
            #raise TimeoutError("timeout while reading acknowledge")

        ## Read answer
        #pyb.delay(50)
        #self.listen()
