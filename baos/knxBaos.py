import pyb
import gc
import select
import struct

import logging
import uasyncio.core as asyncio


# Service code for KNX EMI2
# Reset used for fixed frame telegrams transmitted in packets of length 1
EMI2_L_RESET_IND = 0xA0

# Standard KNX frame, inclusive bus monitor mode!
MAX_FRAME_LENGTH = 128  # max. length of KNX data frame

# Byte position in Object Server Protocol
POS_LENGTH = 0  # length of service
POS_MAIN_SERV = 1  # main service code
POS_SUB_SERV = 2  # sub service code
POS_STR_DP = 3  # start Datapoint
POS_NR_DP = 4  # number of Datapoints
POS_FIRST_DP_ID = 5  # first Datapoint

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

# Defines for object server protocol
BAOS_MAIN_SRV = 0xF0  # main service code for all BAOS services
BAOS_RESET_SRV = 0xa0  # reset/reboot service code

BAOS_SUB_TYPE_MASK = 0xC0  # mask for sub service type
BAOS_SUB_TYPE_REQ = 0x00  # sub service type request
BAOS_SUB_TYPE_RES = 0x80  # sub service type response
BAOS_SUB_TYPE_IND = 0xC0  # sub service type indication


BAOS_GET_SRV_ITEM_REQ = 0x01  # GetServerItem.Req
BAOS_GET_SRV_ITEM_RES = 0x81  # GetServerItem.Res

BAOS_SET_SRV_ITEM_REQ = 0x02  # SetServerItem.Req
BAOS_SET_SRV_ITEM_RES = 0x82  # SetServerItem.Res

BAOS_GET_DP_DESCR_REQ = 0x03  # GetDatapointDescription.Req
BAOS_GET_DP_DESCR_RES = 0x83  # GetDatapointDescription.Res

BAOS_GET_DESCR_STR_REQ = 0x04  # GetDescriptionString.Req
BAOS_GET_DESCR_STR_RES = 0x84  # GetDescriptionString.Res

BAOS_GET_DP_VALUE_REQ = 0x05  # GetDatapointValue.Req
BAOS_GET_DP_VALUE_RES = 0x85  # GetDatapointValue.Res

BAOS_DP_VALUE_IND = 0xC1  # DatapointValue.Ind

BAOS_SET_DP_VALUE_REQ = 0x06  # SetDatapointValue.Req
BAOS_SET_DP_VALUE_RES = 0x86  # SetDatapointValue.Res

BAOS_GET_PARAM_BYTE_REQ = 0x07  # GetParameterByte.Req
BAOS_GET_PARAM_BYTE_RES = 0x87  # GetParameterByte.Res


# Defines for commands used by data point services
DP_CMD_NONE = 0x00  # do nothing
DP_CMD_SET_VAL = 0x01  # change value in data point
DP_CMD_SEND_VAL = 0x02  # send the current value on the bus
DP_CMD_SET_SEND_VAL = 0x03  # change value and send it on the bus
DP_CMD_SEND_READ_VAL = 0x04  # send a value read to the bus
DP_CMD_CLEAR_STATE = 0x05  # clear the state of a data point

# Defines for DatapointDescription configuration flags
DP_DES_FLAG_PRIO = 0x03  # transmit priority
DP_DES_FLAG_COM = 0x04  # Datapoint communication enabled
DP_DES_FLAG_READ = 0x08  # read from bus enabled
DP_DES_FLAG_WRITE = 0x10  # write from bus enabled
DP_DES_FLAG_reserved = 0x20  # reserved
DP_DES_FLAG_CTR = 0x40  # clients transmit request processed
DP_DES_FLAG_UOR = 0x80  # update on response enabled

# Item ID's used in Get-/SetDeviceItem services
ID_NONE = 0
ID_HARDWARE_TYPE = 1
ID_HARDWARE_VER = 2
ID_FIRMWARE_VER = 3
ID_MANUFACT_SYS = 4
ID_MANUFACT_APP = 5
ID_APP_ID = 6
ID_APP_VER = 7
ID_SERIAL_NUM = 8
ID_TIME_RESET = 9
ID_BUS_STATE = 10
ID_MAX_BUFFER = 11
ID_STRG_LEN = 12
ID_BAUDRATE = 13
ID_BUFFER_SIZE = 14
ID_PROG_MODE = 15

# Objects server baud rates
OBJSRV_BAUD_UNKNOWN = 0x00
OBJSRV_BAUD_19K2 = 0x01
OBJSRV_BAUD_115K2 = 0x02
OBJSRV_BAUD_NEW = 0x80

# Buffer size to handle server objects with the FT1.2 driver
OBJ_SERV_BUF_SIZE = MAX_FRAME_LENGTH


class TimeoutError(Exception):
    """
    """


class KnxBaosHandler:
    """
    """


class KnxBaos:
    """
    """
    def __init__(self, uart=2):
        """
        """
        self._uart = pyb.UART(uart)
        self._uart.init(19200, bits=8, parity=0, stop=1)

        self._logger = logging.getLogger("baos")

        self._lastSendFcb_ = 0x00
        self._lastRecvFcb_ = 0x00

    @property
    def _lastSendFcb(self):
        self._lastSendFcb_ ^= FT12_FCB_MASK
        return self._lastSendFcb_

    @property
    def _lastRecvFcb(self):
        self._lastRecvFcb_ ^= FT12_FCB_MASK
        return self._lastRecvFcb_

    def _devodeFrame(self, data):
        """
        """
        header

    def resetDevice(self):
        """ Reset KnxBaos device
        """
        data = chr(FT12_START_FIX_FRAME) + chr(FT12_RESET_REQ) + chr(FT12_RESET_REQ) + chr(FT12_END_CHAR)
        self._logger.debug("KnxBaos.reset(): send data={}".format(repr(data)))
        self._uart.write(data)
        pyb.delay(10)
        ack = self._uart.readchar()
        self._logger.debug("reset: received ack={}".format(hex(ack)))

    @asyncio.coroutine
    def receiveLoop(self):
        """
        """
        while True:
            try:

                # If data available, read complete frame
                if self._uart.any():
                    data = ""
                    while True:
                        c = self._uart.readchar()
                        data += chr(c)
                        if c == FT12_END_CHAR:
                            break

                    # Send ACK
                    self._uart.writechar(FT12_ACK)

                    self._logger.debug("KnxBaos.receiveLoop(): data={}".format(repr(data)))

                    # Decode frame
                    controlField, message = self._decodeFrame(data)

                    # Dispatch service

                asyncio.sleep(10)

            except Exception as e:
                self._logger.debug("KnxBaos.receiveLoop()")
                self._logger.debug(e)


    def getParam(self, first, nb=1):

        # send FT1.2 control field
        #controlField = int('0b10011', 2)
        #controlField |= 1 << 6
        #controlField |= 1 << 7  # 1 = host (application) to BAOS module
                                ## 0 = BAOS module to hos (application)
                                ## Really???!!???
        controlField = 0x53 + self._lastSendFcb


        # Send BAOS message
        main = '\xf0'
        sub = '\x07'
        message = main + sub + chr(first) + chr(nb)

        # Send FT1.2 check sum
        checkSum = controlField
        for c in message:
            checkSum += ord(c)
        checkSum %= 0x100

        # Send data
        data = chr(FT12_START_VAR_FRAME) + chr(len(message)+1) + chr(len(message)+1) + chr(FT12_START_VAR_FRAME) + chr(controlField) + message + chr(checkSum) + chr(FT12_END_CHAR)
        self._logger.debug("getParam: send data={}".format(repr(data)))
        for c in data:
            self._uart.writechar(ord(c))

        # Wait for ack
        pyb.delay(10)
        if self._uart.any():
            ack = self._uart.readchar()
            self._logger.debug("getParam: received ack={}".format(hex(ack)))
        else:
            raise TimeoutError("timeout while reading acknowledge")

        # Read answer
        pyb.delay(50)
        self.listen()


    def getDatapoint(self, first, nb=1):
        # send FT1.2 control field
        #frameCountBit ^= 0x20          # which autmatically toggles at each call
        #controlField |= 1 << 6
        #controlField |= 1 << 7  # 1 = host (application) to BAOS module
                                ## 0 = BAOS module to hos (application)
                                ## Really???!!???
        controlField = 0x53 + self._lastSendFcb

        # Send BAOS message
        main = '\xf0'
        sub = '\x05'
        message = main + sub + chr(first) + chr(nb)

        # Send FT1.2 check sum
        checkSum = controlField
        for c in message:
            checkSum += ord(c)
        checkSum %= 0x100

        # Send data
        data = chr(FT12_START_VAR_FRAME) + chr(len(message)+1) + chr(len(message)+1) + chr(FT12_START_VAR_FRAME) + chr(controlField) + message + chr(checkSum) + chr(FT12_END_CHAR)
        self._logger.debug("getDatapoint: send data={}".format(repr(data)))
        for c in data:
            self._uart.writechar(ord(c))

        # Wait for ack
        pyb.delay(10)
        if self._uart.any():
            ack = self._uart.readchar()
            self._logger.debug("getDatapoint: received ack={}".format(hex(ack)))
        else:
            raise TimeoutError("timeout while reading acknowledge")

        # Read answer
        pyb.delay(50)
        self.listen()


class KnxBaosApplication:
    """
    """





class MyEventLoop(asyncio.EventLoop):
    def time(self):
        return pyb.millis()

    def wait(self, delay):
        asyncio.log.debug("Sleeping for: %s", delay)
        start = pyb.millis()
        while pyb.elapsed_millis(start) < delay:
            gc.collect()
            pyb.delay(10)

asyncio._event_loop_class = MyEventLoop


def main():
    loop = asyncio.get_event_loop()

    baos = KnxBaos()
    baos.reset()

    #baos.getParam(1)
    #baos.getDatapoint(1)

    loop.create_task(baos.receiveLoop())

    loop.run_forever()


if __name__ == "__main__":
    main()
