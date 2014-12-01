# -*- coding: utf-8 -*-

import pyb
import gc
import select
import struct

import logging
import heapq
import uasyncio.core as asyncio

from knxBaosHandler import KnxBaosHandler
from knxBaosFT12 import KnxBaosFT12
from knxBaosTransmission import KnxBaosTransmission


class KnxBaos:
    """
    """
    ## Service code for KNX EMI2
    ## Reset used for fixed frame telegrams transmitted in packets of length 1
    #EMI2_L_RESET_IND = 0xa0

    # Defines for object server protocol
    MAIN_SRV = 0xf0  # main service code for all BAOS services

    #SUB_TYPE_MASK = 0xc0  # mask for sub service type
    #SUB_TYPE_REQ = 0x00  # sub service type request
    #SUB_TYPE_RES = 0x80  # sub service type response
    #SUB_TYPE_IND = 0xc0  # sub service type indication

    GET_SRV_ITEM_REQ = 0x01  # GetServerItem.Req
    SET_SRV_ITEM_REQ = 0x02  # SetServerItem.Req
    #GET_DP_DESCR_REQ = 0x03  # GetDatapointDescription.Req  # replaced by GET_DP_DESCR2_REQ
    GET_DESCR_STR_REQ = 0x04  # GetDescriptionString.Req
    GET_DP_VALUE_REQ = 0x05  # GetDatapointValue.Req
    SET_DP_VALUE_REQ = 0x06  # SetDatapointValue.Req
    GET_PARAM_BYTE_REQ = 0x07  # GetParameterByte.Req
    GET_DP_DESCR2_REQ = 0x08  # GetDatapointDescription2.Req

    # Defines for commands used by data point services
    DP_CMD_NONE = 0x00  # do nothing
    DP_CMD_SET_VAL = 0x01  # change value in data point
    DP_CMD_SEND_VAL = 0x02  # send the current value on the bus
    DP_CMD_SET_SEND_VAL = 0x03  # change value and send it on the bus
    DP_CMD_SEND_READ_VAL = 0x04  # send a value read to the bus
    DP_CMD_CLEAR_STATE = 0x05  # clear the state of a data point

    # Defines for DatapointDescription configuration flags
    DP_DES_FLAG_PRIO_MASK = 0x03  # transmit priority mask
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

    def __init__(self, listener):
        """
        """
        self._handler = KnxBaosHandler(listener)

        self._logger = logging.getLogger("KnxBaos")

        self._inQueue = []
        self._outQueue = []

        self._baosFT12 = KnxBaosFT12(self)

    @asyncio.coroutine
    def _loop(self):
        """ Poll inQueue et appelle handler.receiveCallback()
        """
        while True:
            try:
                message = self._inQueue.pop(0)
                self._handler.receiveCallback(message)
            except IndexError:
                pass
            except Exception as e:
                self._logger.error("_loop(): {}".format(str(e)))

            yield from asyncio.sleep(10)

    def start(self, loop):
        """ Start internal loop
        """
        self._baosFT12.start(loop)

        loop.create_task(self._loop())

    def putInMessage(self, message):
        """ Store message to _inQueue

        Messages are stored in _inQueue by KnxBaosFT12 receiver, and used by KnxBaos loop.
        """
        self._inQueue.append(message)
        #self._logger.debug("putInMessage(): new _inQueue length is {}".format(len(self._inQueue)))

    def getOutMessage(self):
        """ Wait message from _outQueue

        Messages are queued by xxx.Req, and used by KnxBaosFT12 transmitter.
        """
        try:
            return self._outQueue.pop(0)
        except IndexError:
            return None

    @asyncio.coroutine
    def _sendReq(self, message):
        """

        @todo: add logs
        """
        self._logger.debug("_sendReq(): message={}".format(message))

        for i in range(3):
            transmission = KnxBaosTransmission(message)
            self._outQueue.append(transmission)

            while transmission.waitConfirm:
                yield from asyncio.sleep(10)

            if transmission.result == KnxBaosTransmission.OK:
                break
            else:
                self._logger.warning("_sendReq(): transmission failed ({}). retrying...".format(i+1))
                yield from asyncio.sleep(500)
                # !!! FCB should not be toggled when resending frame which has not been ack

        else:
            self._logger.error("_sendReq(): transmission aborted")

        self._logger.debug("_sendReq(): transmission={}".format(transmission))

        return transmission.result

    @asyncio.coroutine
    def getServerItemReq(self, startItem, numberOfItems):
        """
        """
        self._logger.debug("getServerItemReq(): startItem={}, numberOfItems={}".format(startItem, numberOfItems))

        message = (KnxBaos.MAIN_SRV, KnxBaos.GET_SRV_ITEM_REQ, startItem, numberOfItems)
        result = yield from self._sendReq(message)

        return result

    @asyncio.coroutine
    def setServerItemReq(self, itemId, itemData):
        """

        @todo: handle mutliple items settings
        @todo: handle itemData as any type (single value, char, str, tuple...)
        """
        self._logger.debug("setServerItemReq(): itemId={}, itemData={}, args={}".format(itemId, itemData, repr(args)))

        message = (KnxBaos.MAIN_SRV, KnxBaos.SET_SRV_ITEM_REQ, itemId, len(itemData)) + itemData

        result = yield from self._sendReq(message)

        return result

    #@asyncio.coroutine
    #def getDatapointDescriptionReq(self, startDatapoint, numberOfDatapoint):
        #"""
        #"""
        #self._logger.debug("getDatapointDescriptionReq(): startDatapoint={}, numberOfDatapoint={}".format(startDatapoint, numberOfDatapoint))

        #message = (KnxBaos.MAIN_SRV, KnxBaos.GET_DP_DESCR_REQ, startDatapoint, numberOfDatapoint)
        #result = yield from self._sendReq(message)

        #return result

    @asyncio.coroutine
    def getDescriptionStringReq(self, startString, numberOfStrings):
        """
        """
        self._logger.debug("getDescriptionStringReq(): startString={}, numberOfStrings={}".format(startString, numberOfStrings))

        message = (KnxBaos.MAIN_SRV, KnxBaos.GET_DESCR_STR_REQ, startString, numberOfStrings)
        result = yield from self._sendReq(message)

        return result

    @asyncio.coroutine
    def getDatapointValueReq(self, startDatapoint, numberOfDatapoint):
        """
        """
        self._logger.debug("getDatapointValueReq(): startDatapoint={}, numberOfDatapoint={}".format(startDatapoint, numberOfDatapoint))

        message = (KnxBaos.MAIN_SRV, KnxBaos.GET_DP_VALUE_REQ, startDatapoint, numberOfDatapoint)
        result = yield from self._sendReq(message)

        return result

    @asyncio.coroutine
    def setDatapointValueReq(self, dpId, dpCmd, dpData):
        """

        @todo: handle mutliple Datapoint values
        @todo: handle dpData max length
        @todo: use Cmd object
        @todo: handle dpData as any type (single value, char, str, tuple...)
        """
        self._logger.debug("setDatapointValueReq(): dpId={}, dpCmd={}, dpData={}".format(dpId, dpCmd, repr(dpData)))

        cmdLength = dpCmd << 4 | len(dpData) & 0x0f
        message = (KnxBaos.MAIN_SRV, KnxBaos.SET_DP_VALUE_REQ, dpId, cmdLength) + dpData

        result = yield from self._sendReq(message)

        return result

    @asyncio.coroutine
    def getParameterByteReq(self, startByte, numberOfBytes):
        """
        """
        self._logger.debug("getParameterByteReq(): startByte={}, numberOfBytes={}".format(startByte, numberOfBytes))

        message = (KnxBaos.MAIN_SRV, KnxBaos.GET_PARAM_BYTE_REQ, startByte, numberOfBytes)
        result = yield from self._sendReq(message)

        return result

    @asyncio.coroutine
    def getDatapointDescription2Req(self, startDatapoint, numberOfDatapoint):
        """
        """
        self._logger.debug("getDatapointDescription2Req(): startDatapoint={}, numberOfDatapoint={}".format(startDatapoint, numberOfDatapoint))

        message = (KnxBaos.MAIN_SRV, KnxBaos.GET_DP_DESCR2_REQ, startDatapoint, numberOfDatapoint)
        result = yield from self._sendReq(message)

        return result

    def reset(self):
        """ Reset KnxBaos device

        # !!! 2 kind of reset: fix frame length, and std message service...
        """
        self._baosFT12.resetDevice()
