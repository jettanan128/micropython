# -*- coding: utf-8 -*-

import logging


class KnxBaosListener:
    """
    """
    def __init__(self):
        """
        """

        self._logger = logging.getLogger("KnxBaosListener")

    def handleResetInd(self):
        """ Handle reset indication

        What difference with Reset.Ind as fix frame length (0x10 0xc0 0xc0 0x16)?

        BAOS has been reset (could be due to a change of the parameters via ETS).
        """
        pass
        #App_RetrieveParameterBytes()  # request parameter bytes
        #  ->  KnxBaos_GetParameterByte(PB_FIRST, PB_MAX - 1)

    def handleGetServerItemRes(self, itemId, itemData):
        """ Handle the GetServerItem.Res data

        A BAOS message can hold more than one data. This functions gets called for
        every single data in a message array.

        @param itemId: current Item ID from message
        @type itemId: int

        @param itemData: data of current Item from message
        @type itemData: bytearray
        """
        self._logger.debug("handleGetServerItemRes(): itemId={}, itemData={}".format(itemId, repr(itemData)))

    def handleSetServerItemRes(self, startItem):
        """Handle the SetServerItem.Res data

        @param startItem Start Item from message
        @type startItem: int
        """
        self._logger.debug("handleSetServerItemRes(): startItem={}".format(startItem))

    def handleGetDatapointDescriptionRes(self, dpId, dpValueLength, dpConfigFlags):
        """Handle the GetDatapointDescription.Res data

        A BAOS message can hold more than one data. This functions is called
        for every single value (Datapoint) in a message array.

        @param dpId: current Datapoint ID from message
        @type dpId: int

        @param dpValueLength: length of current Datapoint from message
        @type dpValueLength: int

        @param dpConfigFlags: configuration flags of current Datapoint from message
        @type dpConfigFlags: int (or DPConfigFlag object?)
        """
        self._logger.debug("handleGetDatapointDescriptionRes(): dpId={}, dpValueLength={}, dpConfigFlags={}".format(dpId, dpValueLength, dpConfigFlags))

    def handleGetDescriptionStringRes(self, dpId, dpDescriptionStr):
        """Handle the GetDescriptionString.Res data

        A BAOS Message can hold more than one data. This functions gets called for
        every single data in a message array.

        @param dpId: current Datapoint ID from message
        @type dpId: int

        @param dpDescriptionStr: description string of current Datapointfrom message
        @type dpDescriptionStr: str
        """
        self._logger.debug("handleGetDescriptionStringRes(): dpId={}, dpDescriptionStr={}".format(dpId, dpDescriptionStr))

    def handleGetDatapointValueRes(self, dpId, dpState, dpData):
        """ Handle the GetDatapointValue.Res data

        A BAOS Message can hold more than one data. This functions gets called for
        every single data in a message array.

        @param dpId: current Datapoint ID from message
        @type dpId: int

        @param dpState: state of current Datapoint from message
        @type dpState: int (or State object?)

        @param dpData: data of current Datapointfrom message
        @type dpData: bytearray
        """
        self._logger.debug("handleGetDatapointValueRes(): dpId={}, dpState={}, dpData={}".format(dpId, dpState, repr(dpData)))

    def handleDatapointValueInd(self, dpId, dpState, dpData):
        """Handle the DatapointValue.Ind data

        A BAOS Message can hold more than one data. This functions gets called for
        every single data in a message array.

        @param dpId: current Datapoint ID from message
        @type dpId: int

        @param dpState: state of current Datapoint from message
        @type dpState: int (or State object?)

        @param dpData: data of current Datapoint from message
        @type dpData: byte array
        """
        self._logger.debug("handleDatapointValueInd(): dpId={}, dpState={}, dpData={}".format(dpId, dpState, repr(dpData)))

    def handleSetDatapointValueRes(self startDatapoint):
        """ Handle the SetDatapointValue.Res data

        @param startDataPoint: start Datapoint from message
        @type startDataPoint: int
        """
        self._logger.debug("handleSetDatapointValueRes(): startDatapoint={}".format(startDatapoint))

    def handleGetParameterByteRes(self, byteNum, byteData):
        """ Handle the GetParameterByte.Res data

        A BAOS Message can hold more than one data. This functions gets called for
        every single data in a message array.

        @param byteNum: current byte number from message
        @type byteNum: int

        @param byteData: data of current byte from message
        @type byteData: int
        """
        self._logger.debug("handleGetParameterByteRes(): byteNum={}, byteData={}".format(byteNum, byteData))

    def handleGetDatapointDescription2Res(self, dpId, dpValueLength, dpConfigFlags):
        """Handle the GetDatapointDescription2.Res data

        A BAOS message can hold more than one data. This functions is called
        for every single value (Datapoint) in a message array.

        @param dpId: current Datapoint ID from message
        @type dpId: int

        @param dpValueLength: length of current Datapoint from message
        @type dpValueLength: int

        @param dpConfigFlags: configuration flags of current Datapoint from message
        @type dpConfigFlags: int (or DPConfigFlag object?)
        """
        self._logger.debug("handleGetDatapointDescription2Res(): dpId={}, dpValueLength={}, dpConfigFlags={}".format(dpId, dpValueLength, dpConfigFlags))

    def handleError(self, errorCode):
        """ Handle error code

         0 = No error (this function gets never called with that)
         1 = Internal error
         2 = No Item found
         3 = Buffer is too small
         4 = Item is not writable
         5 = Service is not supported
         6 = Bad service parameter
         7 = Wrong Datapoint ID
         8 = Bad Datapoint command
         9 = Bad length of the Datapoint value
        10 = Message inconsistent

        @param errorCode: KNX BAOS ObjectServer error code
        @type errorCode: int
        """
        self._logger.debug("handleError(): errorCode={}".format(errorCode))
