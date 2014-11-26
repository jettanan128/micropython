# -*- coding: utf-8 -*-

import logging

from knxBaos import POS_MAIN_SERV, POS_SUB_SERV

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

BAOS_GET_DP_DESCR2_REQ = 0x08  # GetDatapointDescription2.Req
BAOS_GET_DP_DESCR2_RES = 0x88  # GetDatapointDescription2.Res

# GetServerItem.Res part
GET_SRV_ITEM_POS_START = 2  # start Item position
GET_SRV_ITEM_POS_NR = 3  # number of items position
GET_SRV_ITEM_POS_ERROR = 4  # error ode position
GET_SRV_ITEM_POS_ARRAY = 4  # Item array position
GET_SRV_ITEM_MIN_LEN = 5  # minimum length of message

# SetServerItem.Res part
SET_SRV_ITEM_POS_START = 2  # start Item position
SET_SRV_ITEM_POS_NR = 3  # number of items position
SET_SRV_ITEM_POS_ERROR = 4  # error code position
SET_SRV_ITEM_MIN_LEN = 5  # minimum length of message

# GetDatapointDescription.Res part
GET_DP_DES_POS_START = 3  # start Datapoint position
GET_DP_DES_POS_NR = 3  # number of Datapoints position
GET_DP_DES_POS_ERROR = 4  # error code position
GET_DP_DES_POS_ARRAY = 4  # Datapoint array position
GET_DP_DES_MIN_LEN = 5  # minimum length of message

# GetDescriptionString.Res part
GET_DES_STR_POS_START = 2  # StartString position
GET_DES_STR_POS_NR = 3  # NumberOfStrings position
GET_DES_STR_POS_ERROR = 4  # error code position
GET_DES_STR_POS_ARRAY = 4  # Datapoint array position
GET_DES_STR_MIN_LEN = 5  # minimum length of message

# GetDatapointValue.Res part
GET_DP_VAL_POS_START = 2  # start Datapoint position
GET_DP_VAL_POS_NR = 3  # number of Datapoints position
GET_DP_VAL_POS_ERROR = 4  # error code position
GET_DP_VAL_POS_ARRAY = 4  # Datapoint array position
GET_DP_VAL_MIN_LEN = 5  # minimum length of message

# DatapointValue.Ind part
DP_VAL_POS_START = 2  # start Datapoint position
DP_VAL_POS_NR = 3  # number of Datapoints position
DP_VAL_POS_ARRAY = 4  # Datapoint array position
DP_VAL_MIN_LEN = 5  # minimum length of message

# SetDatapointValue.Res part
SET_DP_VAL_POS_START = 2  # start Datapoint position
SET_DP_VAL_POS_NR = 3  # number of Datapoints position
SET_DP_VAL_POS_ERROR = 4  # error code position
SET_DP_VAL_MIN_LEN = 5  # minimum length of message

# GetParameterByte.Res part
GET_PAR_BYTE_POS_START = 2  # start byte position
GET_PAR_BYTE_POS_NR = 3  # number of bytes position
GET_PAR_BYTE_POS_ERROR = 4  # error code position
GET_PAR_BYTE_POS_ARRAY = 4  # Bytes array position
GET_PAR_BYTE_MIN_LEN = 5  # minimum length of message


class KnxBaosHandler:
    """
    """
    def __init__(self, listener):
        """
        """
        self._listener = listener
        self._logger = logging.getLogger("knxBaosHandler")

    def receiveCallback(self, message):
        """ Handle data received from the BAOS hardware

        @param message: KNX BAOS ObjectServer message
        @type message: byte array
        """

        # Check for reset indication
        if message[POS_MAIN_SERV] == BAOS_RESET_SRV:
            self._listener.handleResetIndication()

        elif message[POS_SUB_SERV] == BAOS_GET_SRV_ITEM_RES:
            self._onGetServerItemRes(message)

        elif message[POS_SUB_SERV] == BAOS_SET_SRV_ITEM_RES:
            self._onSetServerItemRes(message)

        elif message[POS_SUB_SERV] == BAOS_GET_DP_DESCR_RES:
            self._onGetDatapointDescriptionRes(message)

        elif message[POS_SUB_SERV] == BAOS_GET_DESCR_STR_RES:
            self._onGetDescriptionStringRes(message)

        elif message[POS_SUB_SERV] == BAOS_GET_DP_VALUE_RES:
            self._onGetDatapointValueRes(message)

        elif message[POS_SUB_SERV] == BAOS_DP_VALUE_IND:
            self._onDatapointValueInd(message)

        elif message[POS_SUB_SERV] == BAOS_SET_DP_VALUE_RES:
            self._onSetDatapointValueRes(message)

        elif message[POS_SUB_SERV] == BAOS_GET_PARAM_BYTE_RES:
            self._onGetParameterByteRes(message)

        elif message[POS_SUB_SERV] == BAOS_GET_DP_DESCR2_RES:
            self._onGetDatapointDescription2Res(message)

    def _onGetServerItemRes(self, message):
        """Handle the GetServerItem.Res message

        This response is sent by the server as reaction to the GetServerItem
        request. If an error is detected during the request processing server
        send a negative response (number of items == 0).

        @param message: KNX BAOS ObjectServer message
        @type message: byte array
        """

        # Check the length of message
        # Is it usefull? Length should be ok, as we read uart as long as we find the end char...
        if len(message) < GET_SRV_ITEM_MIN_LEN:
            self._logger.error("_onGetServerItemRes(): message too short")
            return

        startItem = message[GET_SRV_ITEM_POS_START]
        numberOfItems = message[GET_SRV_ITEM_POS_NR]
        self._logger.debug("_onGetServerItemRes(): startItem={}, numberOfItems={}".format(startItem, numberOfItems))

        if numberOfItems == 0:
            errorCode = message[GET_SRV_ITEM_POS_ERROR]
            self._logger.error("_onGetServerItemRes(): message error {}".format(errorCode))
            self._listener.handleError(errorCode)  # could also give the startItem, which is in this case the index of bad Item
            return

        # Iterate over all items in service
        index = GET_SRV_ITEM_POS_ARRAY  # point to first Item
        for i in range(numberOfItems):
            itemId = message[index]
            itemDataLength = message[index+1]
            itemData = message[index+2:index+2+itemDataLength]

            # Call listener handler
            self._listener.handleGetServerItemRes(itemId, itemData)

            # Set index to next Item
            index += 2 + itemDataLength

    def _onSetServerItemRes(self, message):
        """ Handle the SetServerItem.Res message

        This response is sent by the server as reaction to the SetServerItem
        request. If an error is detected during the request processing server
        send a negative response (error code != 0).

        @param message: KNX BAOS ObjectServer message
        @type message: byte array
        """

        # Check the length of message
        if len(message) < SET_SRV_ITEM_MIN_LEN:
            self._logger.error("_onSetServerItemRes(): message too short")
            return

        startItem = message[SET_SRV_ITEM_POS_START]
        self._logger.debug("_onSetServerItemRes(): startItem={}".format(startItem))

        errorCode = message[SET_SRV_ITEM_POS_ERROR]
        if errorCode:
            self._logger.error("_onSetServerItemRes(): message error {}".format(errorCode))
            self._listener.handleError(errorCode)
            return

        # Call listener handler
        self._listener.handleSetServerItemRes(startItem)

    def _onGetDatapointDescriptionRes(self, message):
        """ Handle the GetDatapointDescription.Res message

        This response is sent by the server as reaction to the
        GetDatapointDescription request. If an error is detected during the request
        processing, the server sends a negative response
        (number of Datapoints == 0).

        @param message: KNX BAOS ObjectServer message
        @type message: byte array
        """

        # Check the length of message
        if len(message) < GET_DP_DES_MIN_LEN:
            self._logger.error("_onGetDatapointDescriptionRes(): message too short")
            return

        startDatapoint = message[GET_DP_DES_POS_START]
        numberOfDatapoints = message[GET_DP_DES_POS_NR]
        self._logger.debug("_onGetDatapointDescriptionRes(): startDataPoint={}, numberOfDataPoints={}".format(startDatapoint, numberOfDatapoints))

        if numberOfDatapoints == 0:
            errorCode = message[GET_DP_DES_POS_ERROR]
            self._logger.error("_onGetDatapointDescriptionRes(): message error {}".format(errorCode))
            self._listener.handleError(errorCode)
            return

        # Iterate over all Datapoints in service
        index = GET_DP_DES_POS_ARRAY  # point to first Datapoint
        for i in range(numberOfDatapoints):
            dpId = startDatapoint + i
            dpValueLength = message[index]
            dpConfigFlags = message[index+1]

            # Call listener handler
            self._listener.handleGetDatapointDescriptionRes(dpId, dpValueLength, dpConfigFlags)

            # Set index to next Datapoint
            index += 2

    def _onGetDescriptionStringRes(self, message):
        """ Handle the GetDescriptionString.Res message

        This response is sent by the server as reaction to the GetDescriptionString
        request. If an error is detected during the processing of the request, the
        server sends a negative response (number of strings == 0).

        @param message: KNX BAOS ObjectServer message
        @type message: byte array
        """

        # Check the length of message
        if len(message) < GET_DES_STR_MIN_LEN:
            self._logger.error("_onGetDescriptionStringRes(): message too short")
            return

        startString = message[GET_DES_STR_POS_START]
        numberOfStrings = message[GET_DES_STR_POS_NR]
        self._logger.debug("_onGetDescriptionStringRes(): startString={}, numberOfStrings={}".format(startString, numberOfStrings))

        if nNumberOfStrings == 0:
            errorCode = message[GET_DES_STR_POS_ERROR]
            self._logger.error("_onGetDescriptionStringRes(): message error {}".format(errorCode))
            self._listener.handleError(errorCode)
            return

        # Iterate over all Strings in service
        index = GET_DES_STR_POS_ARRAY  # point to first String
        for i in range(nNumberOfStrings):
            dpId = startString + i
            endStr = message[index:].find('\x00')
            dpDescriptionStr = message[index:index+endStr]

            # Call listener handler
            self._listener.handleGetDescriptionStringRes(dpId, dpDescriptionStr)

            # Set index to next String
            index += len(dpDescriptionStr) + 1

    def _onGetDatapointValueRes(self, message):
        """ Handle the GetDatapointValue.Res message

        This response is sent by the server as reaction to the GetDatapointValue
        request. If an error is detected during the processing of the request, the
        server sends a negative response (number of Datapoints == 0).

        @param message: KNX BAOS ObjectServer message
        @type message: byte array
        """

        # Check the length of message
        if len(message) < GET_DP_VAL_MIN_LEN:
            self._logger.error("_onGetDatapointValueRes(): message too short")
            return

        startDatapoint = message[GET_DP_VAL_POS_START]
        numberOfDatapoints = message[GET_DP_VAL_POS_NR]
        self._logger.debug("_onGetDatapointValueRes(): startDatapoint={}, numberOfDatapoints={}".format(startString, numberOfStrings))

        if numberOfDatapoints == 0:
            errorCode = message[GET_DP_VAL_POS_ERROR]
            self._logger.error("_onGetDatapointValueRes(): message error {}".format(errorCode))
            self._listener.handleError(errorCode)
            return

        # Iterate over all Datapoints in service
        index = GET_DP_VAL_POS_ARRAY  # point to first Datapoint
        for i in range(numberOfDatapoints):
            dpId = message[index]
            dpStateLength = message[index+1]
            dpState  = dpStateLength >> 4
            dpLength = dpStateLength & 0x0f
            #@todo: use custom object, like for pKNyX flags

            dpData = message[index+2:index+2+dpLength]

            # Call listener handler
            self._listener.handleGetDatapointValueRes(dpId, dpState, dpData)

            # Set index to next Datapoint
            index += 2 + dpLength

    def _onDatapointValueInd(self, message):
        """ Handle the DatapointValue.Ind message

        This indication is sent asynchronously by the server if the Datapoint(s)
        value is changed.

        @param message: KNX BAOS ObjectServer message
        @type message: byte array
        """

        # Check the length of message
        if len(message) < GET_DP_VAL_MIN_LEN:
            self._logger.error("_onDatapointValueInd(): message too short")
            return

        startDatapoint = message[GET_DP_VAL_POS_START]
        numberOfDatapoints = message[GET_DP_VAL_POS_NR]
        self._logger.debug("_onDatapointValueInd(): startDatapoint={}, numberOfDatapoints={}".format(startDatapoint, numberOfStrings))

        # Iterate over all Datapoints in service
        index = GET_DP_VAL_POS_ARRAY  # point to first Datapoint
        for i in range(numberOfDatapoints):
            dpId = message[index]
            dpStateLength = message[index+1]
            dpState  = dpStateLength >> 4
            dpLength = dpStateLength & 0x0f
            #@todo: use custom object, like for pKNyX flags

            dpData = message[index+2:index+2+dpLength]

            # Call listener handler
            self._listener.handleDatapointValueInd(dpId, dpState, dpData)

            # Set index to next Datapoint
            index += 2 + dpLength

    def _onSetDatapointValueRes(self, message):
        """ Handle the SetDatapointValue.Res message

        This response is sent by the server as reaction to the SetDatapointValue
        request. If an error is detected during the processing of the request, the
        server sends a negative response (error code != 0).

        @param message: KNX BAOS ObjectServer message
        @type message: byte array
        """

        # Check the length of message
        if len(message) < SET_DP_VAL_MIN_LEN:
            self._logger.error("_onSetDatapointValueRes(): message too short")
            return

        startDatapoint = message[SET_DP_VAL_POS_START]
        self._logger.debug("_onSetDatapointValueRes(): startDatapoint={}".format(startDatapoint))

        errorCode = message[SET_DP_VAL_POS_ERROR]
        if errorCode:
            self._logger.error("_onSetDatapointValueRes(): message error {}".format(errorCode))
            self._listener.handleError(errorCode)
            return

        # Call listener handler
        self._listener.handleSetDatapointValueRes(startDatapoint)

    def _onGetParameterByteRes(self, message):
        """ Handle the GetParameterByte.Res message

        This response is sent by the server as reaction to the GetParameterByte
        request. If an error is detected during the request processing server send a
        negative response (number of bytes == 0).

        @param message: KNX BAOS ObjectServer message
        @type message: byte array
        """

        # Check the length of message
        if len(message) < DP_VAL_MIN_LEN:
            self._logger.error("_onGetParameterByteRes(): message too short")
            return

        startByte = message[GET_PAR_BYTE_POS_START]
        numberOfBytes = message[GET_PAR_BYTE_POS_NR]
        self._logger.debug("_onGetParameterByteRes(): startDatapoint={}".format(startDatapoint))

        if numberOfBytes == 0:
            errorCode = message[GET_PAR_BYTE_POS_ERROR]
            self._logger.error("_onGetParameterByteRes(): message error {}".format(errorCode))
            self._listener.handleError(errorCode)
            return

        # Iterate over all Bytes in service
        index = GET_PAR_BYTE_POS_ARRAY  # point to first Byte
        for i in range(numberOfBytes):
            byteData = message[index+i]

            # Call listener handler
            self._listener.handleGetParameterByteRes(startByte+i, byteData)

    def _onGetDatapointDescription2Res(self, message):
        """ Handle the GetDatapointDescription2.Res message

        This response is sent by the server as reaction to the
        GetDatapointDescription request. If an error is detected during the request
        processing, the server sends a negative response
        (number of Datapoints == 0).

        @param message: KNX BAOS ObjectServer message
        @type message: byte array
        """

        # Check the length of message
        if len(message) < GET_DP_DES_MIN_LEN:
            self._logger.error("_onGetDatapointDescription2Res(): message too short")
            return

        startDatapoint = message[GET_DP_DES_POS_START]
        numberOfDatapoints = message[GET_DP_DES_POS_NR]
        self._logger.debug("_onGetDatapointDescription2Res(): startDataPoint={}, numberOfDataPoints={}".format(startDatapoint, numberOfDatapoints))

        if numberOfDatapoints == 0:
            errorCode = message[GET_DP_DES_POS_ERROR]
            self._logger.error("_onGetDatapointDescription2Res(): message error {}".format(errorCode))
            self._listener.handleError(errorCode)
            return

        # Iterate over all Datapoints in service
        index = GET_DP_DES_POS_ARRAY  # point to first Datapoint
        for i in range(numberOfDatapoints):
            dpId = startDatapoint + i
            dpValueLength = message[index]
            dpConfigFlags = message[index+1]

            # Call listener handler
            self._listener.handleGetDatapointDescription2Res(dpId, dpValueLength, dpConfigFlags)

            # Set index to next Datapoint
            index += 2
