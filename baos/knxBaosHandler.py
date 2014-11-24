import struct

from knxBaos import POS_MAIN_SERV, POS_SUB_SERV

# GetServerItem.Res part
GET_SRV_ITEM_POS_START = 3  # start item position
GET_SRV_ITEM_POS_NR = 4  # number of items position
GET_SRV_ITEM_POS_ERROR = 5  # error ode position
GET_SRV_ITEM_POS_ARRAY = 5  # Item array position
GET_SRV_ITEM_MIN_LEN = 5  # minimum length of telegram

# SetServerItem.Res part
SET_SRV_ITEM_POS_START = 3  # start item position
SET_SRV_ITEM_POS_NR = 4  # number of items position
SET_SRV_ITEM_POS_ERROR = 5  # error code position
SET_SRV_ITEM_MIN_LEN = 5  # minimum length of telegram

# GetDatapointDescription.Res part
GET_DP_DES_POS_START = 3  # start Datapoint position
GET_DP_DES_POS_NR = 4  # number of Datapoints position
GET_DP_DES_POS_ERROR = 5  # error code position
GET_DP_DES_POS_ARRAY = 5  # Datapoint array position
GET_DP_DES_MIN_LEN = 5  # minimum length of telegram

# GetDescriptionString.Res part
GET_DES_STR_POS_START = 3  # StartString position
GET_DES_STR_POS_NR = 4  # NumberOfStrings position
GET_DES_STR_POS_ERROR = 5  # error code position
GET_DES_STR_POS_ARRAY = 5  # Datapoint array position
GET_DES_STR_MIN_LEN = 5  # minimum length of telegram

# GetDatapointValue.Res part
GET_DP_VAL_POS_START = 3  # start Datapoint position
GET_DP_VAL_POS_NR = 4  # number of Datapoints position
GET_DP_VAL_POS_ERROR = 5  # error code position
GET_DP_VAL_POS_ARRAY = 5  # Datapoint array position
GET_DP_VAL_MIN_LEN = 5  # minimum length of telegram

# DatapointValue.Ind part
DP_VAL_POS_START = 3  # start Datapoint position
DP_VAL_POS_NR = 4  # number of Datapoints position
DP_VAL_POS_ARRAY = 5  # Datapoint array position
DP_VAL_MIN_LEN = 5  # minimum length of telegram

# SetDatapointValue.Res part
SET_DP_VAL_POS_START = 3  # start Datapoint position
SET_DP_VAL_POS_NR = 4  # number of Datapoints position
SET_DP_VAL_POS_ERROR = 5  # error code position
SET_DP_VAL_MIN_LEN = 5  # minimum length of telegram

# GetParameterByte.Res part
GET_PAR_BYTE_POS_START = 3  # start byte position
GET_PAR_BYTE_POS_NR = 4  # number of bytes position
GET_PAR_BYTE_POS_ERROR = 5  # error code position
GET_PAR_BYTE_POS_ARRAY = 5  # Bytes array position
GET_PAR_BYTE_MIN_LEN = 5  # minimum length of telegram


class KnxBaosHandler:
    """
    """
    def __init__(self, listener):
        """
        """
        self._listener = listener

    def receiveCallback(self, telegram):
        """ Handle data received from the BAOS hardware

        @param telegram: KNX BAOS ObjectServer telegram
                         first entry is length then the actual telegram,
                         see "KNX BAOS ObjectServer Protocol specification"
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
        if telegram[POS_LENGTH] < GET_SRV_ITEM_MIN_LEN:
            return

        startItem = telegram[GET_SRV_ITEM_POS_START]
        nNumberOfItems = telegram[GET_SRV_ITEM_POS_NR]

        if nNumberOfItems == 0:
            errorCode = telegram[GET_SRV_ITEM_POS_ERROR]
            self._listener.handleError(errorCode)
            return

        pData = &telegram[GET_SRV_ITEM_POS_ARRAY]  # set to first Item

        for in i range(nNumberOfItems):  # for all items in service
            itemId            = *pData++  # extract ID of item
            itemDataLength = *pData++  # extract length of item

            self._listener.handleGetServerItemRes(startItem, itemId, itemDataLength, pData)

            pData += itemDataLength  # set pointer to next item

    def _onSetServerItemRes(self, telegram):
        """ Handle the SetServerItem.Res telegram

        This response is sent by the server as reaction to the SetServerItem
        request. If an error is detected during the request processing server
        send a negative response (error code != 0).

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if telegram[POS_LENGTH] < SET_SRV_ITEM_MIN_LEN:
            return

        startItem = telegram[SET_SRV_ITEM_POS_START]
        errorCode = telegram[SET_SRV_ITEM_POS_ERROR]

        if errorCode:
            self._listener.handleError(errorCode)

        else:
            self._listener.handleSetServerItemRes(startItem)

    def _onGetDatapointDescriptionRes(self, telegram):
        """ Handle the GetDatapointDescription.Res telegram

        This response is sent by the server as reaction to the
        GetDatapointDescription request. If an error is detected during the request
        processing, the server sends a negative response
        (number of data points == 0).

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if telegram[POS_LENGTH] < GET_DP_DES_MIN_LEN:
            return

        startDatapoint = telegram[GET_DP_DES_POS_START]
        numberOfDatapoints = telegram[GET_DP_DES_POS_NR]

        if numberOfDatapoints == 0:
            errorCode = telegram[GET_DP_DES_POS_ERROR]
            self._listener.handleError(errorCode)
            return

        pData = &telegram[GET_DP_DES_POS_ARRAY]  # set to first data point

        for in i range(numberOfDatapoints):  # for all data points in service
            nDpValueLength = *pData++  # extract length of data point
            nDpConfigFlags = *pData++  # extract flags of data point

            self._listener.handleGetDatapointDescriptionRes(startDatapoint, nDpValueLength, nDpConfigFlags)

    def _onGetDescriptionStringRes(self, telegram):
        """ Handle the GetDescriptionString.Res telegram

        This response is sent by the server as reaction to the GetDescriptionString
        request. If an error is detected during the processing of the request, the
        server sends a negative response (number of strings == 0).

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if telegram[POS_LENGTH] < GET_DES_STR_MIN_LEN:
            return

        nStartString = telegram[GET_DES_STR_POS_START]
        nNumberOfStrings = telegram[GET_DES_STR_POS_NR]

        if nNumberOfStrings == 0:
            errorCode = telegram[GET_DES_STR_POS_ERROR]
            self._listener.handleError(errorCode)
            return

        pData = &telegram[GET_DES_STR_POS_ARRAY]  # set to first string

        for i in range(nNumberOfStrings):  # for all strings in service
            strDpDescription = pData

            for(nDpDescriptionLength = 0 *pData++ != 0 nDpDescriptionLength++):  # extract flags of string
                pass

            self._listener.handleGetDescriptionStringRes(nStartString, strDpDescription, nDpDescriptionLength)

    def _onGetDatapointValueRes(self, telegram):
        """ Handle the GetDatapointValue.Res telegram

        This response is sent by the server as reaction to the GetDatapointValue
        request. If an error is detected during the processing of the request, the
        server sends a negative response (number of data points == 0).

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if telegram[POS_LENGTH] < GET_DP_VAL_MIN_LEN:
            return

        startDatapoint = telegram[GET_DP_VAL_POS_START]
        numberOfDatapoints = telegram[GET_DP_VAL_POS_NR]

        if numberOfDatapoints == 0:
            errorCode = telegram[GET_DP_VAL_POS_ERROR]
            self._listener.handleError(errorCode)
            return

        pData = &telegram[GET_DP_VAL_POS_ARRAY]  # set to first data point

        for in i range(numberOfDatapoints):  # for all data points in service
            dpId      = *pData++  # extract ID of data point
            dpState  = (*pData) >> 4  # extract state of data point
            dpLength = (*pData++) & 0x0f  # extract length of data point

            self._listener.handleGetDatapointValueRes(startDatapoint, dpId, dpState, dpLength, pData)

            pData += dpLength  # set pointer to next item




    def _onDatapointValueInd(self, telegram):
        """ Handle the DatapointValue.Ind telegram

        This indication is sent asynchronously by the server if the data point(s)
        value is changed.

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if telegram[POS_LENGTH] < DP_VAL_MIN_LEN:
            return

        numberOfDatapoints = telegram[DP_VAL_POS_NR]
        pData = &telegram[DP_VAL_POS_ARRAY]

        for in i range(numberOfDatapoints):  # for all data points in service
            dpId      = *pData++  # extract ID of data point
            dpState  = (*pData) >> 4  # extract state of data point
            dpLength = (*pData++) & 0x0f  # extract length of data point

            self._listener.handleDatapointValueInd(dpId, dpState, dpLength, pData)

            pData += dpLength  # set pointer to next item




    def _onSetDatapointValueRes(self, telegram):
        """ Handle the SetDatapointValue.Res telegram

        This response is sent by the server as reaction to the SetDatapointValue
        request. If an error is detected during the processing of the request, the
        server sends a negative response (error code != 0).

        @param telegram: KNX BAOS ObjectServer telegram
        @type telegram: byte array
        """

        # Check the length of telegram
        if telegram[POS_LENGTH] < SET_DP_VAL_MIN_LEN:
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
        if telegram[POS_LENGTH] < DP_VAL_MIN_LEN:
            return

        nStartByte = telegram[GET_PAR_BYTE_POS_START]
        nNumberOfBytes = telegram[GET_PAR_BYTE_POS_NR]

        if nNumberOfBytes == 0:
            errorCode = telegram[GET_PAR_BYTE_POS_ERROR]
            self._listener.handleError(errorCode)
            return

        pData = &telegram[GET_PAR_BYTE_POS_ARRAY]  # set to first byte

        for i in range(nNumberOfBytes):  # for all bytes in service
            nByte = *pData++  # extract ID of data point
            self._listener.handleGetParameterByteRes(nStartByte+i, nByte)
