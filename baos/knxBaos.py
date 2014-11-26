# -*- coding: utf-8 -*-

import pyb
import gc
import select
import struct

import logging
import heapq
import uasyncio.core as asyncio

from knxBaosTransmission import KnxBaosTransmission

# Service code for KNX EMI2
# Reset used for fixed frame telegrams transmitted in packets of length 1
EMI2_L_RESET_IND = 0xa0

# Byte position in Object Server Protocol
POS_MAIN_SERV = 0  # main service code
POS_SUB_SERV = 1  # sub service code

# Defines for object server protocol
BAOS_MAIN_SRV = 0xf0  # main service code for all BAOS services
BAOS_RESET_SRV = 0xa0  # reset/reboot service code

BAOS_SUB_TYPE_MASK = 0xc0  # mask for sub service type
BAOS_SUB_TYPE_REQ = 0x00  # sub service type request
BAOS_SUB_TYPE_RES = 0x80  # sub service type response
BAOS_SUB_TYPE_IND = 0xc0  # sub service type indication


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

BAOS_DP_VALUE_IND = 0xc1  # DatapointValue.Ind

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

# Item ID's used in Get/SetDeviceItem services
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


class KnxBaos:
    """
    """
    def __init__(self, listener):
        """
        """
        self._handler = KnxBaosHandler(listener)

        self._inQueue = []
        self._outQueue = []

        self._baosFT12 = KnxBaosFT12(self)

    @asyncio.coroutine
    def _loop(self):
        """ Poll inQueue et appelle handler.receiveCallback()
        """
        while True:
            #message = self._inQueue.pop(0)

            asyncio.sleep(10)

    def start(self, loop):
        """ Start internal loop
        """
        self._baosFT12.start()

        loop.add_task(self._loop())

    def putInMessage(self, message):
        """ Store message to _inQueue
        """
        self._inQueue.append(message)

    @asyncio.coroutine
    def getOutMessage(self):
        """ Attend un message depuis _outQueue

        Les messages sont mis par les .Req, reset...
        """
        while len(self._outQueue) == 0:
            yield from asyncio.sleep(10)

        return self._outQueue.pop(0)

    @asyncio.coroutine
    def _sendReq(self, message):
        """
        """
        transmission = KnxBaosTransmission(message)
        self._outQueue.append(transmission)

        while transmission.waitConfirm:
            yield from asyncio.sleep(10)

        return transmission.result

    def getServerItemReq(self, startItem, numberOfItems):
        """

        @todo: manage for wait confirm, retry...
        """
        message = (BAOS_MAIN_SRV, BAOS_GET_SRV_ITEM_REQ, startItem, numberOfItems)

        return self._sendReq(message)

    def reset(self):
        """ Reset KnxBaos device

        #! 2 kind of reset: fix frame length, and std message service...
        """
        self._baosFT12.resetDevice()
