import struct

import logging

from knxBaos import POS_MAIN_SERV, POS_SUB_SERV

# GetServerItem.Res part
GET_SRV_ITEM_POS_START = 2  # start Item position
GET_SRV_ITEM_POS_NR = 3  # number of items position
GET_SRV_ITEM_POS_ERROR = 4  # error ode position
GET_SRV_ITEM_POS_ARRAY = 4  # Item array position
GET_SRV_ITEM_MIN_LEN = 5  # minimum length of telegram

# SetServerItem.Res part
SET_SRV_ITEM_POS_START = 2  # start Item position
SET_SRV_ITEM_POS_NR = 3  # number of items position
SET_SRV_ITEM_POS_ERROR = 4  # error code position
SET_SRV_ITEM_MIN_LEN = 5  # minimum length of telegram

# GetDatapointDescription.Res part
GET_DP_DES_POS_START = 3  # start Datapoint position
GET_DP_DES_POS_NR = 3  # number of Datapoints position
GET_DP_DES_POS_ERROR = 4  # error code position
GET_DP_DES_POS_ARRAY = 4  # Datapoint array position
GET_DP_DES_MIN_LEN = 5  # minimum length of telegram

# GetDescriptionString.Res part
GET_DES_STR_POS_START = 2  # StartString position
GET_DES_STR_POS_NR = 3  # NumberOfStrings position
GET_DES_STR_POS_ERROR = 4  # error code position
GET_DES_STR_POS_ARRAY = 4  # Datapoint array position
GET_DES_STR_MIN_LEN = 5  # minimum length of telegram

# GetDatapointValue.Res part
GET_DP_VAL_POS_START = 2  # start Datapoint position
GET_DP_VAL_POS_NR = 3  # number of Datapoints position
GET_DP_VAL_POS_ERROR = 4  # error code position
GET_DP_VAL_POS_ARRAY = 4  # Datapoint array position
GET_DP_VAL_MIN_LEN = 5  # minimum length of telegram

# DatapointValue.Ind part
DP_VAL_POS_START = 2  # start Datapoint position
DP_VAL_POS_NR = 3  # number of Datapoints position
DP_VAL_POS_ARRAY = 4  # Datapoint array position
DP_VAL_MIN_LEN = 5  # minimum length of telegram

# SetDatapointValue.Res part
SET_DP_VAL_POS_START = 2  # start Datapoint position
SET_DP_VAL_POS_NR = 3  # number of Datapoints position
SET_DP_VAL_POS_ERROR = 4  # error code position
SET_DP_VAL_MIN_LEN = 5  # minimum length of telegram

# GetParameterByte.Res part
GET_PAR_BYTE_POS_START = 2  # start byte position
GET_PAR_BYTE_POS_NR = 3  # number of bytes position
GET_PAR_BYTE_POS_ERROR = 4  # error code position
GET_PAR_BYTE_POS_ARRAY = 4  # Bytes array position
GET_PAR_BYTE_MIN_LEN = 5  # minimum length of telegram


class KnxBaosHandler:
    """
    """
    def __init__(self, listener):
        """
        """
        self._listener = listener
        self._logger = logging.getLogger("knxBaosHandler")

    def receiveCallback(self, telegram):
        """ Handle data received from the BAOS hardware

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check for reset indication
        if telegram[POS_MAIN_SERV] == BAOS_RESET_SRV:
            self._listener.handleResetIndication()

        elif telegram[POS_SUB_SERV] == BAOS_GET_SRV_ITEM_RES:
            self._onGetServerItemRes(telegram)

        elif telegram[POS_SUB_SERV] == BAOS_SET_SRV_ITEM_RES:
            self._onSetServerItemRes(telegram)

        elif telegram[POS_SUB_SERV] == BAOS_GET_DP_DESCR_RES:
            self._onGetDatapointDescriptionRes(telegram)

        elif telegram[POS_SUB_SERV] == BAOS_GET_DESCR_STR_RES:
            self._onGetDescriptionStringRes(telegram)

        elif telegram[POS_SUB_SERV] == BAOS_GET_DP_VALUE_RES:
            self._onGetDatapointValueRes(telegram)

        elif telegram[POS_SUB_SERV] == BAOS_DP_VALUE_IND:
            self._onDatapointValueInd(telegram)

        elif telegram[POS_SUB_SERV] == BAOS_SET_DP_VALUE_RES:
            self._onSetDatapointValueRes(telegram)

        elif telegram[POS_SUB_SERV] == BAOS_GET_PARAM_BYTE_RES:
            self._onGetParameterByteRes(telegram)

    def _onGetServerItemRes(self, telegram):
        """Handle the GetServerItem.Res telegram

        This response is sent by the server as reaction to the GetServerItem
        request. If an error is detected during the request processing server
        send a negative response (number of items == 0).

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        # Is it usefull? Length should be ok, as we read uart as long as we find the end char...
        if len(telegram) < GET_SRV_ITEM_MIN_LEN:
            self._logger.error("_onGetServerItemRes(): telegram too short")
            return

        startItem = telegram[GET_SRV_ITEM_POS_START]
        numberOfItems = telegram[GET_SRV_ITEM_POS_NR]
        self._logger.debug("_onGetServerItemRes(): startItem={}, numberOfItems={}".format(startItem, numberOfItems))

        if numberOfItems == 0:
            errorCode = telegram[GET_SRV_ITEM_POS_ERROR]
            self._logger.error("_onGetServerItemRes(): telegram error {}".format(errorCode))
            self._listener.handleError(errorCode)  # could also give the startItem, which is in this case the index of bad Item
            return

        #@todo: check telegram length against number of items? Or let error happens with struct?

        # Iterate over all items in service
        index = GET_SRV_ITEM_POS_ARRAY  # point to first Item
        for i in range(numberOfItems):
            itemId = telegram[index]
            itemDataLength = telegram[index+1]
            itemData = struct.unpack(itemDataLength*'B', telegram[index+2:])

            # Call listener handler
            self._listener.handleGetServerItemRes(itemId, itemData)

            # Set index to next Item
            index += 2 + itemDataLength

    def _onSetServerItemRes(self, telegram):
        """ Handle the SetServerItem.Res telegram

        This response is sent by the server as reaction to the SetServerItem
        request. If an error is detected during the request processing server
        send a negative response (error code != 0).

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if len(telegram) < SET_SRV_ITEM_MIN_LEN:
            self._logger.error("_onSetServerItemRes(): telegram too short")
            return

        startItem = telegram[SET_SRV_ITEM_POS_START]
        errorCode = telegram[SET_SRV_ITEM_POS_ERROR]
        self._logger.debug("_onSetServerItemRes(): startDataPoint={}, numberOfDataPoints={}".format(startDatapoint, numberOfDatapoints))

        if errorCode:
            self._logger.error("_onSetServerItemRes(): telegram error {}".format(errorCode))
            self._listener.handleError(errorCode)
            return

        # Call listener handler
        self._listener.handleSetServerItemRes(startItem)

    def _onGetDatapointDescriptionRes(self, telegram):
        """ Handle the GetDatapointDescription.Res telegram

        This response is sent by the server as reaction to the
        GetDatapointDescription request. If an error is detected during the request
        processing, the server sends a negative response
        (number of Datapoints == 0).

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if len(telegram) < GET_DP_DES_MIN_LEN:
            self._logger.error("_onGetDatapointDescriptionRes(): telegram too short")
            return

        startDatapoint = telegram[GET_DP_DES_POS_START]
        numberOfDatapoints = telegram[GET_DP_DES_POS_NR]
        self._logger.debug("_onGetDatapointDescriptionRes(): startDataPoint={}, numberOfDataPoints={}".format(startDatapoint, numberOfDatapoints))

        if numberOfDatapoints == 0:
            errorCode = telegram[GET_DP_DES_POS_ERROR]
            self._logger.error("_onGetDatapointDescriptionRes(): telegram error {}".format(errorCode))
            self._listener.handleError(errorCode)
            return

        # Iterate over all Datapoints in service
        index = GET_DP_DES_POS_ARRAY  # point to first Datapoint
        for i in range(numberOfDatapoints):
            dpId = startDatapoint + i
            dpValueLength = telegram[index]
            dpConfigFlags = telegram[index+1]

            # Call listener handler
            self._listener.handleGetDatapointDescriptionRes(dpId, dpValueLength, dpConfigFlags)

            # Set index to next Datapoint
            index += 2

    def _onGetDescriptionStringRes(self, telegram):
        """ Handle the GetDescriptionString.Res telegram

        This response is sent by the server as reaction to the GetDescriptionString
        request. If an error is detected during the processing of the request, the
        server sends a negative response (number of strings == 0).

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if len(telegram) < GET_DES_STR_MIN_LEN:
            self._logger.error("_onGetDescriptionStringRes(): telegram too short")
            return

        startString = telegram[GET_DES_STR_POS_START]
        numberOfStrings = telegram[GET_DES_STR_POS_NR]
        self._logger.debug("_onGetDescriptionStringRes(): startString={}, numberOfStrings={}".format(startString, numberOfStrings))

        if nNumberOfStrings == 0:
            errorCode = telegram[GET_DES_STR_POS_ERROR]
            self._logger.error("_onGetDescriptionStringRes(): telegram error {}".format(errorCode))
            self._listener.handleError(errorCode)
            return

        # Iterate over all Strings in service
        index = GET_DES_STR_POS_ARRAY  # point to first String
        for i in range(nNumberOfStrings):
            dpId = startString + i
            endStr = telegram[index:].find('\x00')
            dpDescriptionStr = telegram[index:index+endStr]

            # Call listener handler
            self._listener.handleGetDescriptionStringRes(dpId, dpDescriptionStr)

            # Set index to next String
            index += len(dpDescriptionStr) + 1

    def _onGetDatapointValueRes(self, telegram):
        """ Handle the GetDatapointValue.Res telegram

        This response is sent by the server as reaction to the GetDatapointValue
        request. If an error is detected during the processing of the request, the
        server sends a negative response (number of Datapoints == 0).

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if len(telegram) < GET_DP_VAL_MIN_LEN:
            self._logger.error("_onGetDatapointValueRes(): telegram too short")
            return

        startDatapoint = telegram[GET_DP_VAL_POS_START]
        numberOfDatapoints = telegram[GET_DP_VAL_POS_NR]
        self._logger.debug("_onGetDatapointValueRes(): startDatapoint={}, numberOfDatapoints={}".format(startString, numberOfStrings))

        if numberOfDatapoints == 0:
            errorCode = telegram[GET_DP_VAL_POS_ERROR]
            self._logger.error("_onGetDatapointValueRes(): telegram error {}".format(errorCode))
            self._listener.handleError(errorCode)
            return

        # Iterate over all Datapoints in service
        index = GET_DP_VAL_POS_ARRAY  # point to first Datapoint
        for i in range(numberOfDatapoints):
            dpId = telegram[index]
            dpStateLength = telegram[index+1]
            dpState  = dpStateLength >> 4
            dpLength = dpStateLength & 0x0f
            #@todo: use custom object, like for pKNyX flags

            dpData = telegram[index+2:index+2+dpLength]

            # Call listener handler
            self._listener.handleGetDatapointValueRes(dpId, dpState, dpData)

            # Set index to next Datapoint
            index += 2 + dpLength




    def _onDatapointValueInd(self, telegram):
        """ Handle the DatapointValue.Ind telegram

        This indication is sent asynchronously by the server if the Datapoint(s)
        value is changed.

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if len(telegram) < DP_VAL_MIN_LEN:
            return

        numberOfDatapoints = telegram[DP_VAL_POS_NR]
        data = &telegram[DP_VAL_POS_ARRAY]

        for i in range(numberOfDatapoints):  # for all Datapoints in service
            dpId      = *data++  # extract ID of Datapoint
            dpState  = (*data) >> 4  # extract state of Datapoint
            dpLength = (*data++) & 0x0f  # extract length of Datapoint

            self._listener.handleDatapointValueInd(dpId, dpState, dpLength, data)

            data += dpLength  # set pointer to next Item




    def _onSetDatapointValueRes(self, telegram):
        """ Handle the SetDatapointValue.Res telegram

        This response is sent by the server as reaction to the SetDatapointValue
        request. If an error is detected during the processing of the request, the
        server sends a negative response (error code != 0).

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if len(telegram) < SET_DP_VAL_MIN_LEN:
            return

        startDatapoint = telegram[SET_DP_VAL_POS_START]
        errorCode = telegram[SET_DP_VAL_POS_ERROR]

        if errorCode:
            self._listener.handleError(errorCode)
            return

        self._listener.handleSetDatapointValueRes(startDatapoint)

    def _onGetParameterByteRes(self, telegram):
        """ Handle the GetParameterByte.Res telegram

        This response is sent by the server as reaction to the GetParameterByte
        request. If an error is detected during the request processing server send a
        negative response (number of bytes == 0).

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if len(telegram) < DP_VAL_MIN_LEN:
            return

        nStartByte = telegram[GET_PAR_BYTE_POS_START]
        nNumberOfBytes = telegram[GET_PAR_BYTE_POS_NR]

        if nNumberOfBytes == 0:
            errorCode = telegram[GET_PAR_BYTE_POS_ERROR]
            self._listener.handleError(errorCode)
            return

        data = &telegram[GET_PAR_BYTE_POS_ARRAY]  # set to first byte

        for i in range(nNumberOfBytes):  # for all bytes in service
            nByte = *data++  # extract ID of Datapoint
            self._listener.handleGetParameterByteRes(nStartByte+i, nByte)
